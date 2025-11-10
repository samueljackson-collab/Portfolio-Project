import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import '../models/tab_model.dart';
import '../utils/constants.dart';

/// AI Service for tab classification using TensorFlow Lite
class AIService {
  Interpreter? _interpreter;
  bool _isInitialized = false;

  /// Initialize the TensorFlow Lite model
  Future<void> initialize() async {
    try {
      // Load the model from assets
      _interpreter = await Interpreter.fromAsset('assets/models/tab_classifier.tflite');
      _isInitialized = true;
      print('AI Service initialized successfully');
    } catch (e) {
      print('Error initializing AI Service: $e');
      _isInitialized = false;
    }
  }

  /// Classify a tab using AI/ML model
  Future<Map<String, dynamic>> classifyTab(TabModel tab) async {
    if (!_isInitialized) {
      return _fallbackClassification(tab);
    }

    try {
      // Extract features from tab
      final features = _extractFeatures(tab);

      // Run inference
      final output = List.filled(AppConstants.defaultCategories.length, 0.0).reshape([1, AppConstants.defaultCategories.length]);
      _interpreter!.run([features], output);

      // Get category with highest confidence
      final scores = output[0] as List<double>;
      final maxIndex = scores.indexOf(scores.reduce((a, b) => a > b ? a : b));
      final category = AppConstants.defaultCategories[maxIndex];
      final confidence = scores[maxIndex];

      return {
        'category': category,
        'confidence': confidence,
        'scores': Map.fromIterables(
          AppConstants.defaultCategories,
          scores,
        ),
      };
    } catch (e) {
      print('Error classifying tab: $e');
      return _fallbackClassification(tab);
    }
  }

  /// Extract features from tab for ML model
  /// Must match the 15 features expected by the trained model
  List<double> _extractFeatures(TabModel tab) {
    final features = <double>[];

    // URL features
    final url = tab.url.toLowerCase();
    final domain = tab.domain ?? '';
    final title = tab.title.toLowerCase();

    // Domain-based features (one-hot encoding) - 6 features
    // Must match order in Python training: work, research, shopping, social, entertainment, news
    final categories = ['work', 'research', 'shopping', 'social', 'entertainment', 'news'];
    for (final category in categories) {
      final patterns = AppConstants.categoryPatterns[category] ?? [];
      final match = patterns.any((pattern) =>
        domain.contains(pattern) || url.contains(pattern)
      );
      features.add(match ? 1.0 : 0.0);
    }

    // Keyword-based features (normalized counts) - 6 features
    // Must match order in Python training: work, research, shopping, social, entertainment, news
    final keywordSets = {
      'work': ['github', 'code', 'dev', 'api', 'docs', 'documentation', 'programming'],
      'research': ['research', 'study', 'paper', 'journal', 'academic', 'scholar'],
      'shopping': ['buy', 'shop', 'cart', 'price', 'order', 'product'],
      'social': ['facebook', 'twitter', 'instagram', 'social', 'friend', 'post'],
      'entertainment': ['video', 'watch', 'movie', 'music', 'play', 'stream'],
      'news': ['news', 'article', 'breaking', 'latest', 'report'],
    };

    for (final category in categories) {
      final keywords = keywordSets[category] ?? [];
      final score = _countKeywords(title, keywords) / keywords.length;
      features.add(score);
    }

    // URL structure features - 3 features
    features.add(url.split('/').length.toDouble() / 10); // Path depth (normalized)
    features.add(url.contains('?') ? 1.0 : 0.0); // Has query params
    features.add(url.contains('#') ? 1.0 : 0.0); // Has fragment

    // Total: 6 + 6 + 3 = 15 features (matches Python training script)
    assert(features.length == 15, 'Feature count must be 15, got ${features.length}');
    return features;
  }

  /// Count keyword matches in text
  double _countKeywords(String text, List<String> keywords) {
    return keywords.where((keyword) => text.contains(keyword)).length.toDouble();
  }

  /// Fallback classification using pattern matching
  Map<String, dynamic> _fallbackClassification(TabModel tab) {
    final url = tab.url.toLowerCase();
    final domain = tab.domain ?? '';

    // Check URL patterns
    for (final entry in AppConstants.categoryPatterns.entries) {
      for (final pattern in entry.value) {
        if (domain.contains(pattern) || url.contains(pattern)) {
          return {
            'category': entry.key,
            'confidence': 0.8,
            'method': 'pattern_matching',
          };
        }
      }
    }

    // Default to 'custom' category
    return {
      'category': 'custom',
      'confidence': 0.5,
      'method': 'default',
    };
  }

  /// Batch classify multiple tabs
  Future<List<Map<String, dynamic>>> classifyTabs(List<TabModel> tabs) async {
    final results = <Map<String, dynamic>>[];

    for (final tab in tabs) {
      final result = await classifyTab(tab);
      results.add(result);
    }

    return results;
  }

  /// Train the model with user feedback
  Future<void> trainWithFeedback({
    required TabModel tab,
    required String correctCategory,
  }) async {
    // In a production app, this would collect training data
    // and periodically retrain the model
    print('Training feedback: ${tab.url} -> $correctCategory');

    // Store feedback for later model retraining
    // Implementation would involve:
    // 1. Store feedback in local database
    // 2. Periodically batch upload to server
    // 3. Retrain model with new data
    // 4. Download updated model
  }

  /// Get category suggestions based on partial input
  List<String> getCategorySuggestions(String query) {
    final lowerQuery = query.toLowerCase();
    return AppConstants.defaultCategories
        .where((category) => category.contains(lowerQuery))
        .toList();
  }

  /// Analyze tab content for better classification
  Future<Map<String, dynamic>> analyzeContent(String content) async {
    // NLP analysis of tab content
    // This would extract keywords, topics, entities, etc.

    final keywords = _extractKeywords(content);
    final topics = _identifyTopics(keywords);

    return {
      'keywords': keywords,
      'topics': topics,
      'language': 'en', // Simplified - would use language detection
    };
  }

  List<String> _extractKeywords(String content) {
    // Simple keyword extraction
    final words = content.toLowerCase().split(RegExp(r'\W+'));
    final wordFreq = <String, int>{};

    for (final word in words) {
      if (word.length > 3) {
        wordFreq[word] = (wordFreq[word] ?? 0) + 1;
      }
    }

    // Return top keywords
    final sortedWords = wordFreq.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return sortedWords.take(10).map((e) => e.key).toList();
  }

  List<String> _identifyTopics(List<String> keywords) {
    final topics = <String>[];

    // Simple topic identification based on keyword clusters
    final techKeywords = ['code', 'api', 'dev', 'github', 'programming'];
    final socialKeywords = ['friend', 'post', 'share', 'like', 'comment'];
    final newsKeywords = ['news', 'article', 'report', 'breaking', 'update'];

    if (keywords.any((k) => techKeywords.contains(k))) topics.add('technology');
    if (keywords.any((k) => socialKeywords.contains(k))) topics.add('social');
    if (keywords.any((k) => newsKeywords.contains(k))) topics.add('news');

    return topics;
  }

  /// Dispose resources
  void dispose() {
    _interpreter?.close();
    _isInitialized = false;
  }
}
