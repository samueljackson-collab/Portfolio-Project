import 'dart:math';
import 'package:logger/logger.dart';
import 'package:uuid/uuid.dart';

import '../config/app_config.dart';
import '../models/tab.dart';
import '../models/tab_group.dart';

/// DBSCAN-based tab clustering service
class TabClusterer {
  final Logger _logger = Logger();
  final Uuid _uuid = const Uuid();

  /// Cluster tabs by category using DBSCAN algorithm
  List<TabGroup> clusterTabs(List<Tab> tabs, TabCategory category) {
    if (tabs.length < AppConfig.clusteringMinSamples) {
      // Not enough tabs to cluster
      return _createSingleGroup(tabs, category);
    }

    _logger.d('Clustering ${tabs.length} tabs in category: ${category.displayName}');

    // Calculate pairwise similarity matrix
    final similarityMatrix = _calculateSimilarityMatrix(tabs);

    // Run DBSCAN clustering
    final clusters = _dbscan(
      tabs.length,
      similarityMatrix,
      AppConfig.clusteringEpsilon,
      AppConfig.clusteringMinSamples,
    );

    // Convert clusters to tab groups
    final groups = clusters.map((cluster) {
      final clusterTabs = cluster.map((i) => tabs[i]).toList();
      return _createGroup(clusterTabs, category);
    }).toList();

    _logger.d('Created ${groups.length} groups');
    return groups;
  }

  /// Calculate similarity matrix for all tab pairs
  List<List<double>> _calculateSimilarityMatrix(List<Tab> tabs) {
    final n = tabs.length;
    final matrix = List.generate(n, (_) => List.filled(n, 0.0));

    for (int i = 0; i < n; i++) {
      for (int j = i; j < n; j++) {
        if (i == j) {
          matrix[i][j] = 1.0;
        } else {
          final similarity = _calculateSimilarity(tabs[i], tabs[j]);
          matrix[i][j] = similarity;
          matrix[j][i] = similarity;
        }
      }
    }

    return matrix;
  }

  /// Calculate similarity between two tabs
  double _calculateSimilarity(Tab tab1, Tab tab2) {
    // Domain similarity (same domain = high similarity)
    final domainSim = tab1.domain == tab2.domain ? 1.0 : 0.0;

    // Temporal proximity (opened within 5 minutes = high similarity)
    final timeDiff = tab1.createdAt.difference(tab2.createdAt).inMinutes.abs();
    final temporalSim = timeDiff < 5 ? 1.0 : max(0.0, 1.0 - timeDiff / 60.0);

    // Title similarity (Jaccard index of words)
    final titleSim = _jaccardSimilarity(
      _tokenize(tab1.title),
      _tokenize(tab2.title),
    );

    // URL path similarity
    final path1 = Uri.tryParse(tab1.url)?.pathSegments ?? [];
    final path2 = Uri.tryParse(tab2.url)?.pathSegments ?? [];
    final pathSim = _jaccardSimilarity(path1.toSet(), path2.toSet());

    // Weighted average
    return 0.4 * domainSim +
           0.2 * temporalSim +
           0.3 * titleSim +
           0.1 * pathSim;
  }

  /// Jaccard similarity coefficient
  double _jaccardSimilarity(Set<String> set1, Set<String> set2) {
    if (set1.isEmpty && set2.isEmpty) return 1.0;
    if (set1.isEmpty || set2.isEmpty) return 0.0;

    final intersection = set1.intersection(set2).length;
    final union = set1.union(set2).length;

    return intersection / union;
  }

  /// Tokenize text into words
  Set<String> _tokenize(String text) {
    return text
        .toLowerCase()
        .split(RegExp(r'[^\w]+'))
        .where((word) => word.length > 2)
        .toSet();
  }

  /// DBSCAN clustering algorithm
  List<List<int>> _dbscan(
    int numPoints,
    List<List<double>> similarityMatrix,
    double epsilon,
    int minSamples,
  ) {
    final labels = List.filled(numPoints, -1);  // -1 = unvisited
    final clusters = <List<int>>[];
    int clusterId = 0;

    for (int i = 0; i < numPoints; i++) {
      if (labels[i] != -1) continue;  // Already visited

      // Find neighbors
      final neighbors = _getNeighbors(i, similarityMatrix, epsilon);

      if (neighbors.length < minSamples) {
        labels[i] = -2;  // Mark as noise
        continue;
      }

      // Start new cluster
      clusters.add([]);
      _expandCluster(
        i,
        neighbors,
        clusterId,
        labels,
        similarityMatrix,
        epsilon,
        minSamples,
        clusters[clusterId],
      );

      clusterId++;
    }

    return clusters;
  }

  /// Get neighbors within epsilon distance
  List<int> _getNeighbors(
    int point,
    List<List<double>> similarityMatrix,
    double epsilon,
  ) {
    final neighbors = <int>[];

    for (int i = 0; i < similarityMatrix.length; i++) {
      if (similarityMatrix[point][i] >= epsilon) {
        neighbors.add(i);
      }
    }

    return neighbors;
  }

  /// Expand cluster from seed point
  void _expandCluster(
    int point,
    List<int> neighbors,
    int clusterId,
    List<int> labels,
    List<List<double>> similarityMatrix,
    double epsilon,
    int minSamples,
    List<int> cluster,
  ) {
    labels[point] = clusterId;
    cluster.add(point);

    final queue = List<int>.from(neighbors);

    while (queue.isNotEmpty) {
      final current = queue.removeAt(0);

      if (labels[current] == -2) {
        // Change noise to border point
        labels[current] = clusterId;
        cluster.add(current);
      }

      if (labels[current] != -1) continue;  // Already processed

      labels[current] = clusterId;
      cluster.add(current);

      final currentNeighbors = _getNeighbors(
        current,
        similarityMatrix,
        epsilon,
      );

      if (currentNeighbors.length >= minSamples) {
        queue.addAll(currentNeighbors);
      }
    }
  }

  /// Create a TabGroup from clustered tabs
  TabGroup _createGroup(List<Tab> tabs, TabCategory category) {
    final groupName = _generateGroupName(tabs, category);

    return TabGroup(
      id: _uuid.v4(),
      name: groupName,
      category: category,
      tabIds: tabs.map((t) => t.id).toList(),
      createdAt: DateTime.now(),
    );
  }

  /// Create single group for small tab sets
  List<TabGroup> _createSingleGroup(List<Tab> tabs, TabCategory category) {
    if (tabs.isEmpty) return [];

    return [_createGroup(tabs, category)];
  }

  /// Generate smart group name based on tab content
  String _generateGroupName(List<Tab> tabs, TabCategory category) {
    if (tabs.isEmpty) return category.displayName;

    // Find common domain
    final domains = tabs.map((t) => t.domain).toSet();
    if (domains.length == 1) {
      // All tabs from same domain
      final domain = domains.first;
      final siteName = _extractSiteName(domain);
      return '$siteName - ${category.displayName}';
    }

    // Find common keywords in titles
    final allWords = <String, int>{};
    for (final tab in tabs) {
      for (final word in _tokenize(tab.title)) {
        allWords[word] = (allWords[word] ?? 0) + 1;
      }
    }

    // Get most frequent meaningful words
    final commonWords = allWords.entries
        .where((e) => e.value > tabs.length * 0.5)  // In >50% of tabs
        .where((e) => !_stopWords.contains(e.key))
        .map((e) => e.key)
        .take(3)
        .toList();

    if (commonWords.isNotEmpty) {
      final keywords = commonWords.map(_capitalize).join(' ');
      return '$keywords - ${category.displayName}';
    }

    // Fallback: use category and count
    return '${category.displayName} (${tabs.length} tabs)';
  }

  /// Extract readable site name from domain
  String _extractSiteName(String domain) {
    // Remove www and TLD
    var name = domain.replaceFirst('www.', '');
    name = name.split('.').first;
    return _capitalize(name);
  }

  /// Capitalize first letter
  String _capitalize(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }

  /// Common stop words to filter out
  static const Set<String> _stopWords = {
    'the', 'and', 'for', 'with', 'you', 'this', 'that',
    'from', 'are', 'was', 'has', 'have', 'more', 'how',
  };
}
