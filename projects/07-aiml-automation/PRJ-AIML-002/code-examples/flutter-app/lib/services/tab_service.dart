import 'package:hive/hive.dart';
import 'package:uuid/uuid.dart';
import '../models/tab_model.dart';
import '../utils/constants.dart';

/// Service for managing tabs and tab groups
class TabService {
  late Box<TabModel> _tabsBox;
  late Box<TabGroup> _groupsBox;
  bool _isInitialized = false;

  /// Initialize the tab service
  Future<void> initialize() async {
    try {
      _tabsBox = await Hive.openBox<TabModel>('tabs');
      _groupsBox = await Hive.openBox<TabGroup>('tab_groups');
      _isInitialized = true;
      print('Tab Service initialized successfully');
    } catch (e) {
      print('Error initializing Tab Service: $e');
    }
  }

  /// Add a new tab
  Future<TabModel> addTab({
    required String title,
    required String url,
    String? faviconUrl,
    required String category,
    double confidenceScore = 0.0,
    required String browser,
    int tabIndex = 0,
    bool isPinned = false,
  }) async {
    final uuid = const Uuid();
    final now = DateTime.now();

    final tab = TabModel(
      id: uuid.v4(),
      title: title,
      url: url,
      faviconUrl: faviconUrl,
      category: category,
      confidenceScore: confidenceScore,
      createdAt: now,
      lastAccessed: now,
      browser: browser,
      tabIndex: tabIndex,
      isPinned: isPinned,
      domain: _extractDomain(url),
    );

    await _tabsBox.put(tab.id, tab);
    return tab;
  }

  /// Get all tabs
  List<TabModel> getAllTabs() {
    if (!_isInitialized) return [];
    return _tabsBox.values.toList();
  }

  /// Get tabs by category
  List<TabModel> getTabsByCategory(String category) {
    if (!_isInitialized) return [];
    return _tabsBox.values
        .where((tab) => tab.category == category)
        .toList();
  }

  /// Get tabs by group
  List<TabModel> getTabsByGroup(String groupId) {
    if (!_isInitialized) return [];
    return _tabsBox.values
        .where((tab) => tab.groupId == groupId)
        .toList();
  }

  /// Update tab
  Future<void> updateTab(TabModel tab) async {
    await _tabsBox.put(tab.id, tab);
  }

  /// Delete tab
  Future<void> deleteTab(String tabId) async {
    await _tabsBox.delete(tabId);
  }

  /// Create tab group
  Future<TabGroup> createGroup({
    required String name,
    required String category,
    List<String>? tabIds,
    String? colorHex,
  }) async {
    final uuid = const Uuid();
    final now = DateTime.now();

    final group = TabGroup(
      id: uuid.v4(),
      name: name,
      category: category,
      tabIds: tabIds ?? [],
      colorHex: colorHex ?? _getCategoryColor(category),
      createdAt: now,
      updatedAt: now,
      sortOrder: _groupsBox.length,
    );

    await _groupsBox.put(group.id, group);
    return group;
  }

  /// Get all groups
  List<TabGroup> getAllGroups() {
    if (!_isInitialized) return [];
    return _groupsBox.values.toList()
      ..sort((a, b) => a.sortOrder.compareTo(b.sortOrder));
  }

  /// Get group by ID
  TabGroup? getGroupById(String groupId) {
    return _groupsBox.get(groupId);
  }

  /// Update group
  Future<void> updateGroup(TabGroup group) async {
    final updatedGroup = group.copyWith(updatedAt: DateTime.now());
    await _groupsBox.put(updatedGroup.id, updatedGroup);
  }

  /// Delete group
  Future<void> deleteGroup(String groupId) async {
    // Remove group reference from tabs
    final tabsInGroup = getTabsByGroup(groupId);
    for (final tab in tabsInGroup) {
      await updateTab(tab.copyWith(groupId: null));
    }

    await _groupsBox.delete(groupId);
  }

  /// Add tab to group
  Future<void> addTabToGroup(String tabId, String groupId) async {
    final tab = _tabsBox.get(tabId);
    final group = _groupsBox.get(groupId);

    if (tab != null && group != null) {
      // Update tab
      await updateTab(tab.copyWith(groupId: groupId));

      // Update group
      if (!group.tabIds.contains(tabId)) {
        final updatedTabIds = [...group.tabIds, tabId];
        await updateGroup(group.copyWith(tabIds: updatedTabIds));
      }
    }
  }

  /// Remove tab from group
  Future<void> removeTabFromGroup(String tabId, String groupId) async {
    final tab = _tabsBox.get(tabId);
    final group = _groupsBox.get(groupId);

    if (tab != null && group != null) {
      // Update tab
      await updateTab(tab.copyWith(groupId: null));

      // Update group
      final updatedTabIds = group.tabIds.where((id) => id != tabId).toList();
      await updateGroup(group.copyWith(tabIds: updatedTabIds));
    }
  }

  /// Auto-group tabs by category
  Future<void> autoGroupTabs() async {
    final tabs = getAllTabs();
    final categoryCounts = <String, int>{};

    // Count tabs per category
    for (final tab in tabs) {
      categoryCounts[tab.category] = (categoryCounts[tab.category] ?? 0) + 1;
    }

    // Create groups for categories with multiple tabs
    for (final entry in categoryCounts.entries) {
      if (entry.value > 1) {
        final categoryTabs = getTabsByCategory(entry.key);

        // Check if group already exists
        final existingGroups = _groupsBox.values
            .where((g) => g.category == entry.key)
            .toList();

        TabGroup group;
        if (existingGroups.isEmpty) {
          // Create new group
          group = await createGroup(
            name: _getCategoryName(entry.key),
            category: entry.key,
          );
        } else {
          group = existingGroups.first;
        }

        // Add tabs to group
        for (final tab in categoryTabs) {
          if (tab.groupId == null) {
            await addTabToGroup(tab.id, group.id);
          }
        }
      }
    }
  }

  /// Search tabs
  List<TabModel> searchTabs(String query) {
    if (!_isInitialized || query.isEmpty) return [];

    final lowerQuery = query.toLowerCase();
    return _tabsBox.values.where((tab) {
      return tab.title.toLowerCase().contains(lowerQuery) ||
          tab.url.toLowerCase().contains(lowerQuery) ||
          tab.category.toLowerCase().contains(lowerQuery);
    }).toList();
  }

  /// Find duplicate tabs
  List<List<TabModel>> findDuplicates() {
    final tabs = getAllTabs();
    final urlMap = <String, List<TabModel>>{};

    // Group by URL
    for (final tab in tabs) {
      urlMap.putIfAbsent(tab.url, () => []).add(tab);
    }

    // Return groups with duplicates
    return urlMap.values.where((group) => group.length > 1).toList();
  }

  /// Remove duplicate tabs (keep most recent)
  Future<void> removeDuplicates() async {
    final duplicates = findDuplicates();

    for (final group in duplicates) {
      // Sort by last accessed (most recent first)
      group.sort((a, b) => b.lastAccessed.compareTo(a.lastAccessed));

      // Delete all except the first (most recent)
      for (var i = 1; i < group.length; i++) {
        await deleteTab(group[i].id);
      }
    }
  }

  /// Get tabs by browser
  List<TabModel> getTabsByBrowser(String browser) {
    if (!_isInitialized) return [];
    return _tabsBox.values
        .where((tab) => tab.browser == browser)
        .toList();
  }

  /// Get recently accessed tabs
  List<TabModel> getRecentTabs({int limit = 20}) {
    if (!_isInitialized) return [];

    final tabs = _tabsBox.values.toList()
      ..sort((a, b) => b.lastAccessed.compareTo(a.lastAccessed));

    return tabs.take(limit).toList();
  }

  /// Clear all tabs
  Future<void> clearAllTabs() async {
    await _tabsBox.clear();
  }

  /// Clear all groups
  Future<void> clearAllGroups() async {
    await _groupsBox.clear();
  }

  /// Extract domain from URL
  String _extractDomain(String url) {
    try {
      final uri = Uri.parse(url);
      return uri.host;
    } catch (e) {
      return '';
    }
  }

  /// Get category color
  String _getCategoryColor(String category) {
    final color = AppConstants.categoryColors[category] ??
        AppConstants.categoryColors['custom']!;
    return color.value.toRadixString(16).padLeft(8, '0');
  }

  /// Get category name
  String _getCategoryName(String category) {
    return category[0].toUpperCase() + category.substring(1);
  }

  /// Export tabs to JSON
  Map<String, dynamic> exportTabs() {
    return {
      'tabs': getAllTabs().map((tab) => tab.toJson()).toList(),
      'groups': getAllGroups().map((group) => group.toJson()).toList(),
      'exportedAt': DateTime.now().toIso8601String(),
      'version': AppConstants.appVersion,
    };
  }

  /// Import tabs from JSON
  Future<void> importTabs(Map<String, dynamic> data) async {
    try {
      final tabs = (data['tabs'] as List)
          .map((json) => TabModel.fromJson(json))
          .toList();

      final groups = (data['groups'] as List)
          .map((json) => TabGroup.fromJson(json))
          .toList();

      // Import tabs
      for (final tab in tabs) {
        await _tabsBox.put(tab.id, tab);
      }

      // Import groups
      for (final group in groups) {
        await _groupsBox.put(group.id, group);
      }

      print('Imported ${tabs.length} tabs and ${groups.length} groups');
    } catch (e) {
      print('Error importing tabs: $e');
      rethrow;
    }
  }
}
