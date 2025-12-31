import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive/hive.dart';
import 'package:url_launcher/url_launcher.dart';

import '../services/sync_service.dart';

/// Home screen with tab group management
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _selectedIndex = 0;
  final SyncService _syncService = SyncService();

  @override
  void initState() {
    super.initState();
    _initializeSettings();
  }

  Future<void> _initializeSettings() async {
    final settings = await Hive.openBox('settings');
    final autoSyncEnabled =
        settings.get('autoSyncEnabled', defaultValue: true) as bool;
    final cloudSyncEnabled =
        settings.get('cloudSyncEnabled', defaultValue: true) as bool;
    if (autoSyncEnabled && cloudSyncEnabled) {
      _syncService.startAutoSync();
    }
  }

  @override
  void dispose() {
    _syncService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tab Organizer'),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: _onSyncPressed,
            tooltip: 'Sync',
          ),
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: _onSearchPressed,
            tooltip: 'Search',
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _onSettingsPressed,
            tooltip: 'Settings',
          ),
        ],
      ),
      body: _buildBody(),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.tab),
            label: 'Tabs',
          ),
          NavigationDestination(
            icon: Icon(Icons.folder),
            label: 'Groups',
          ),
          NavigationDestination(
            icon: Icon(Icons.insights),
            label: 'Insights',
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _onOrganizePressed,
        icon: const Icon(Icons.auto_awesome),
        label: const Text('Organize'),
      ),
    );
  }

  Widget _buildBody() {
    switch (_selectedIndex) {
      case 0:
        return _buildTabsView();
      case 1:
        return _buildGroupsView();
      case 2:
        return _buildInsightsView();
      default:
        return _buildTabsView();
    }
  }

  Widget _buildTabsView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.tab,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No tabs yet',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Open some browser tabs to get started',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _onOrganizePressed,
            icon: const Icon(Icons.auto_awesome),
            label: const Text('Organize Tabs'),
          ),
        ],
      ),
    );
  }

  Widget _buildGroupsView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.folder_outlined,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No groups yet',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Organize your tabs to create groups',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightsView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.insights,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          const Text(
            'No insights yet',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Use the app to see your browsing insights',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }

  void _onOrganizePressed() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Organizing tabs...'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  Future<void> _onSyncPressed() async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Syncing...'),
        duration: Duration(seconds: 1),
      ),
    );

    final result = await _syncService.sync();
    if (!mounted) return;

    final message = result.success
        ? 'Synced ${result.tabsUploaded + result.tabsDownloaded} tabs '
            'and ${result.groupsUploaded + result.groupsDownloaded} groups'
        : 'Sync failed: ${result.error}';

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  Future<void> _onSearchPressed() async {
    final items = await _loadSearchItems();
    if (!mounted) return;
    await showSearch(
      context: context,
      delegate: TabSearchDelegate(items: items),
    );
  }

  Future<void> _onSettingsPressed() async {
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => SettingsScreen(syncService: _syncService),
      ),
    );
  }

  Future<List<SearchItem>> _loadSearchItems() async {
    final tabsBox = await Hive.openBox<Map>('tabs');
    final groupsBox = await Hive.openBox<Map>('tab_groups');

    final tabItems = tabsBox.values.map((value) {
      final data = Map<String, dynamic>.from(value);
      return SearchItem(
        type: SearchItemType.tab,
        id: data['id']?.toString() ?? '',
        title: data['title']?.toString() ?? 'Untitled',
        subtitle: data['url']?.toString() ?? '',
        description: data['description']?.toString(),
        metadata: data,
      );
    });

    final groupItems = groupsBox.values.map((value) {
      final data = Map<String, dynamic>.from(value);
      return SearchItem(
        type: SearchItemType.group,
        id: data['id']?.toString() ?? '',
        title: data['name']?.toString() ?? 'Untitled Group',
        subtitle: data['category']?.toString() ?? 'Uncategorized',
        description: data['description']?.toString(),
        metadata: data,
      );
    });

    return [...tabItems, ...groupItems].toList();
  }
}

enum SearchItemType { tab, group }

class SearchItem {
  SearchItem({
    required this.type,
    required this.id,
    required this.title,
    required this.subtitle,
    this.description,
    this.metadata,
  });

  final SearchItemType type;
  final String id;
  final String title;
  final String subtitle;
  final String? description;
  final Map<String, dynamic>? metadata;

  String get searchableText => [
        title,
        subtitle,
        description ?? '',
      ].join(' ').toLowerCase();
}

class TabSearchDelegate extends SearchDelegate {
  TabSearchDelegate({required this.items});

  final List<SearchItem> items;

  @override
  List<Widget>? buildActions(BuildContext context) {
    return [
      if (query.isNotEmpty)
        IconButton(
          icon: const Icon(Icons.clear),
          onPressed: () => query = '',
        ),
    ];
  }

  @override
  Widget? buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () => close(context, null),
    );
  }

  @override
  Widget buildResults(BuildContext context) {
    final results = _filterItems();
    if (results.isEmpty) {
      return const Center(child: Text('No matching tabs found.'));
    }

    return ListView.builder(
      itemCount: results.length,
      itemBuilder: (context, index) {
        final tab = results[index];
        return ListTile(
          leading: Icon(
            tab.type == SearchItemType.tab ? Icons.tab : Icons.folder,
          ),
          title: Text(tab.title),
          subtitle: Text(tab.subtitle),
          onTap: () => close(context, tab.metadata),
        );
      },
    );
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    final suggestions = _filterItems(limit: 5);
    if (suggestions.isEmpty) {
      return const Center(child: Text('Search your tabs and groups.'));
    }

    return ListView.builder(
      itemCount: suggestions.length,
      itemBuilder: (context, index) {
        final tab = suggestions[index];
        return ListTile(
          leading: Icon(
            tab.type == SearchItemType.tab ? Icons.search : Icons.folder,
          ),
          title: Text(tab.title),
          subtitle: Text(tab.subtitle),
          onTap: () {
            query = tab.title;
            showResults(context);
          },
        );
      },
    );
  }

  List<SearchItem> _filterItems({int? limit}) {
    final normalizedQuery = query.toLowerCase().trim();
    if (normalizedQuery.isEmpty) {
      return limit != null ? items.take(limit).toList() : items;
    }

    final filtered = items
        .where((item) => item.searchableText.contains(normalizedQuery))
        .toList();

    return limit != null ? filtered.take(limit).toList() : filtered;
  }
}

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key, required this.syncService});

  final SyncService syncService;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _autoSyncEnabled = true;
  bool _cloudSyncEnabled = true;
  bool _wifiOnlySync = false;
  bool _notificationsEnabled = true;
  bool _biometricsEnabled = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final box = await Hive.openBox('settings');
    setState(() {
      _autoSyncEnabled =
          box.get('autoSyncEnabled', defaultValue: true) as bool;
      _cloudSyncEnabled =
          box.get('cloudSyncEnabled', defaultValue: true) as bool;
      _wifiOnlySync = box.get('wifiOnlySync', defaultValue: false) as bool;
      _notificationsEnabled =
          box.get('notificationsEnabled', defaultValue: true) as bool;
      _biometricsEnabled =
          box.get('biometricsEnabled', defaultValue: false) as bool;
    });
  }

  Future<void> _updateSetting(String key, bool value) async {
    final box = await Hive.openBox('settings');
    await box.put(key, value);
  }

  Future<void> _openDesktopApp() async {
    const uri = Uri.parse('taborganizer://open?source=mobile');
    final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!launched && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Desktop app not available.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        children: [
          SwitchListTile(
            title: const Text('Cloud sync'),
            subtitle: const Text('Enable Firebase sync across devices'),
            value: _cloudSyncEnabled,
            onChanged: (value) async {
              setState(() => _cloudSyncEnabled = value);
              await _updateSetting('cloudSyncEnabled', value);
              if (!value) {
                widget.syncService.stopAutoSync();
              } else if (_autoSyncEnabled) {
                widget.syncService.startAutoSync();
              }
            },
          ),
          SwitchListTile(
            title: const Text('Auto-sync'),
            subtitle: const Text('Keep tabs synced in the background'),
            value: _autoSyncEnabled,
            onChanged: (value) async {
              setState(() => _autoSyncEnabled = value);
              await _updateSetting('autoSyncEnabled', value);
              if (value && _cloudSyncEnabled) {
                widget.syncService.startAutoSync();
              } else {
                widget.syncService.stopAutoSync();
              }
            },
          ),
          SwitchListTile(
            title: const Text('Sync on Wi-Fi only'),
            subtitle: const Text('Avoid syncing over cellular data'),
            value: _wifiOnlySync,
            onChanged: (value) async {
              setState(() => _wifiOnlySync = value);
              await _updateSetting('wifiOnlySync', value);
            },
          ),
          SwitchListTile(
            title: const Text('Notifications'),
            subtitle: const Text('Get alerts for new group suggestions'),
            value: _notificationsEnabled,
            onChanged: (value) async {
              setState(() => _notificationsEnabled = value);
              await _updateSetting('notificationsEnabled', value);
            },
          ),
          SwitchListTile(
            title: const Text('Biometric unlock'),
            subtitle: const Text('Require biometrics for sensitive actions'),
            value: _biometricsEnabled,
            onChanged: (value) async {
              setState(() => _biometricsEnabled = value);
              await _updateSetting('biometricsEnabled', value);
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.desktop_windows),
            title: const Text('Open desktop app'),
            subtitle: const Text('Launch the desktop companion'),
            onTap: _openDesktopApp,
          ),
        ],
      ),
    );
  }
}
