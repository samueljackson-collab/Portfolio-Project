import 'package:flutter/foundation.dart';
import '../models/tab_model.dart';
import '../services/tab_service.dart';
import '../services/ai_service.dart';
import '../services/sync_service.dart';

/// Provider for managing tab state
class TabProvider with ChangeNotifier {
  final TabService _tabService = TabService();
  final AIService _aiService = AIService();
  final SyncService _syncService = SyncService();

  List<TabModel> _tabs = [];
  List<TabGroup> _groups = [];
  TabModel? _selectedTab;
  TabGroup? _selectedGroup;
  bool _isLoading = false;
  String? _error;
  String _searchQuery = '';

  // Getters
  List<TabModel> get tabs => _searchQuery.isEmpty
      ? _tabs
      : _tabs.where((tab) =>
            tab.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            tab.url.toLowerCase().contains(_searchQuery.toLowerCase())).toList();

  List<TabGroup> get groups => _groups;
  TabModel? get selectedTab => _selectedTab;
  TabGroup? get selectedGroup => _selectedGroup;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String get searchQuery => _searchQuery;

  /// Initialize provider
  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _tabService.initialize();
      await _aiService.initialize();
      await _syncService.initialize();

      await loadTabs();
      await loadGroups();

      _error = null;
    } catch (e) {
      _error = 'Failed to initialize: $e';
      debugPrint(_error);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Load all tabs
  Future<void> loadTabs() async {
    try {
      _tabs = _tabService.getAllTabs();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load tabs: $e';
      debugPrint(_error);
    }
  }

  /// Load all groups
  Future<void> loadGroups() async {
    try {
      _groups = _tabService.getAllGroups();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load groups: $e';
      debugPrint(_error);
    }
  }

  /// Add a new tab
  Future<void> addTab({
    required String title,
    required String url,
    String? faviconUrl,
    required String browser,
    int tabIndex = 0,
    bool isPinned = false,
  }) async {
    try {
      // Create tab with initial category
      final tab = await _tabService.addTab(
        title: title,
        url: url,
        faviconUrl: faviconUrl,
        category: 'custom',
        browser: browser,
        tabIndex: tabIndex,
        isPinned: isPinned,
      );

      // Classify tab using AI
      final classification = await _aiService.classifyTab(tab);
      final updatedTab = tab.copyWith(
        category: classification['category'],
        confidenceScore: classification['confidence'],
      );

      await _tabService.updateTab(updatedTab);
      await loadTabs();

      _error = null;
    } catch (e) {
      _error = 'Failed to add tab: $e';
      debugPrint(_error);
    }
  }

  /// Update tab
  Future<void> updateTab(TabModel tab) async {
    try {
      await _tabService.updateTab(tab);
      await loadTabs();
      _error = null;
    } catch (e) {
      _error = 'Failed to update tab: $e';
      debugPrint(_error);
    }
  }

  /// Delete tab
  Future<void> deleteTab(String tabId) async {
    try {
      await _tabService.deleteTab(tabId);
      await loadTabs();
      _error = null;
    } catch (e) {
      _error = 'Failed to delete tab: $e';
      debugPrint(_error);
    }
  }

  /// Create a new group
  Future<void> createGroup({
    required String name,
    required String category,
    List<String>? tabIds,
    String? colorHex,
  }) async {
    try {
      await _tabService.createGroup(
        name: name,
        category: category,
        tabIds: tabIds,
        colorHex: colorHex,
      );
      await loadGroups();
      _error = null;
    } catch (e) {
      _error = 'Failed to create group: $e';
      debugPrint(_error);
    }
  }

  /// Update group
  Future<void> updateGroup(TabGroup group) async {
    try {
      await _tabService.updateGroup(group);
      await loadGroups();
      _error = null;
    } catch (e) {
      _error = 'Failed to update group: $e';
      debugPrint(_error);
    }
  }

  /// Delete group
  Future<void> deleteGroup(String groupId) async {
    try {
      await _tabService.deleteGroup(groupId);
      await loadGroups();
      await loadTabs();
      _error = null;
    } catch (e) {
      _error = 'Failed to delete group: $e';
      debugPrint(_error);
    }
  }

  /// Add tab to group
  Future<void> addTabToGroup(String tabId, String groupId) async {
    try {
      await _tabService.addTabToGroup(tabId, groupId);
      await loadTabs();
      await loadGroups();
      _error = null;
    } catch (e) {
      _error = 'Failed to add tab to group: $e';
      debugPrint(_error);
    }
  }

  /// Remove tab from group
  Future<void> removeTabFromGroup(String tabId, String groupId) async {
    try {
      await _tabService.removeTabFromGroup(tabId, groupId);
      await loadTabs();
      await loadGroups();
      _error = null;
    } catch (e) {
      _error = 'Failed to remove tab from group: $e';
      debugPrint(_error);
    }
  }

  /// Auto-group tabs
  Future<void> autoGroupTabs() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _tabService.autoGroupTabs();
      await loadTabs();
      await loadGroups();
      _error = null;
    } catch (e) {
      _error = 'Failed to auto-group tabs: $e';
      debugPrint(_error);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Reclassify all tabs
  Future<void> reclassifyAllTabs() async {
    _isLoading = true;
    notifyListeners();

    try {
      for (final tab in _tabs) {
        final classification = await _aiService.classifyTab(tab);
        final updatedTab = tab.copyWith(
          category: classification['category'],
          confidenceScore: classification['confidence'],
        );
        await _tabService.updateTab(updatedTab);
      }

      await loadTabs();
      _error = null;
    } catch (e) {
      _error = 'Failed to reclassify tabs: $e';
      debugPrint(_error);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Search tabs
  void searchTabs(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  /// Clear search
  void clearSearch() {
    _searchQuery = '';
    notifyListeners();
  }

  /// Select tab
  void selectTab(TabModel? tab) {
    _selectedTab = tab;
    notifyListeners();
  }

  /// Select group
  void selectGroup(TabGroup? group) {
    _selectedGroup = group;
    notifyListeners();
  }

  /// Get tabs by category
  List<TabModel> getTabsByCategory(String category) {
    return _tabs.where((tab) => tab.category == category).toList();
  }

  /// Get tabs by group
  List<TabModel> getTabsByGroup(String groupId) {
    return _tabs.where((tab) => tab.groupId == groupId).toList();
  }

  /// Find duplicates
  List<List<TabModel>> findDuplicates() {
    return _tabService.findDuplicates();
  }

  /// Remove duplicates
  Future<void> removeDuplicates() async {
    try {
      await _tabService.removeDuplicates();
      await loadTabs();
      _error = null;
    } catch (e) {
      _error = 'Failed to remove duplicates: $e';
      debugPrint(_error);
    }
  }

  /// Sync with cloud
  Future<void> syncWithCloud() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _syncService.syncAll();
      await loadTabs();
      await loadGroups();
      _error = null;
    } catch (e) {
      _error = 'Failed to sync: $e';
      debugPrint(_error);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Export tabs
  Map<String, dynamic> exportTabs() {
    return _tabService.exportTabs();
  }

  /// Import tabs
  Future<void> importTabs(Map<String, dynamic> data) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _tabService.importTabs(data);
      await loadTabs();
      await loadGroups();
      _error = null;
    } catch (e) {
      _error = 'Failed to import tabs: $e';
      debugPrint(_error);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Get statistics
  Map<String, dynamic> getStatistics() {
    final categoryCount = <String, int>{};
    for (final tab in _tabs) {
      categoryCount[tab.category] = (categoryCount[tab.category] ?? 0) + 1;
    }

    return {
      'totalTabs': _tabs.length,
      'totalGroups': _groups.length,
      'categoryCounts': categoryCount,
      'ungroupedTabs': _tabs.where((tab) => tab.groupId == null).length,
      'pinnedTabs': _tabs.where((tab) => tab.isPinned).length,
    };
  }

  @override
  void dispose() {
    _aiService.dispose();
    _syncService.dispose();
    super.dispose();
  }
}
