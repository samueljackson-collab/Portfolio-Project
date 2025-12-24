import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/tab_provider.dart';
import '../providers/settings_provider.dart';
import '../models/tab_model.dart';
import '../utils/constants.dart';

/// Main home screen displaying tabs and groups
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<TabProvider>().initialize();
      context.read<SettingsProvider>().initialize();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(context),
      body: Consumer<TabProvider>(
        builder: (context, tabProvider, child) {
          if (tabProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (tabProvider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    'Error: ${tabProvider.error}',
                    style: const TextStyle(color: Colors.red),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => tabProvider.initialize(),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          return Row(
            children: [
              _buildSidebar(context, tabProvider),
              Expanded(child: _buildMainContent(context, tabProvider)),
            ],
          );
        },
      ),
      floatingActionButton: _buildFAB(context),
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context) {
    return AppBar(
      title: Row(
        children: [
          Icon(Icons.tab, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 8),
          const Text(AppConstants.appName),
        ],
      ),
      actions: [
        // Search
        IconButton(
          icon: const Icon(Icons.search),
          onPressed: () => _showSearchDialog(context),
          tooltip: 'Search tabs',
        ),
        // Auto-group
        IconButton(
          icon: const Icon(Icons.auto_awesome),
          onPressed: () {
            context.read<TabProvider>().autoGroupTabs();
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Auto-grouping tabs...')),
            );
          },
          tooltip: 'Auto-group tabs',
        ),
        // Sync
        IconButton(
          icon: const Icon(Icons.sync),
          onPressed: () {
            context.read<TabProvider>().syncWithCloud();
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Syncing...')),
            );
          },
          tooltip: 'Sync with cloud',
        ),
        // Settings
        IconButton(
          icon: const Icon(Icons.settings),
          onPressed: () => _showSettingsDialog(context),
          tooltip: 'Settings',
        ),
      ],
    );
  }

  Widget _buildSidebar(BuildContext context, TabProvider tabProvider) {
    return Container(
      width: 250,
      color: Theme.of(context).colorScheme.surfaceVariant,
      child: Column(
        children: [
          // Statistics
          _buildStatisticsCard(context, tabProvider),
          const Divider(height: 1),

          // Categories
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(8),
              children: [
                const Padding(
                  padding: EdgeInsets.all(8),
                  child: Text(
                    'Categories',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                ...AppConstants.defaultCategories.map((category) {
                  final count = tabProvider
                      .getTabsByCategory(category)
                      .length;
                  return ListTile(
                    dense: true,
                    leading: Icon(
                      _getCategoryIcon(category),
                      color: AppConstants.categoryColors[category],
                    ),
                    title: Text(_capitalize(category)),
                    trailing: Chip(
                      label: Text('$count'),
                      backgroundColor:
                          AppConstants.categoryColors[category]?.withOpacity(0.2),
                    ),
                    onTap: () {
                      // Filter by category
                    },
                  );
                }),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatisticsCard(BuildContext context, TabProvider tabProvider) {
    final stats = tabProvider.getStatistics();

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Overview',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            _buildStatRow('Total Tabs', '${stats['totalTabs']}'),
            _buildStatRow('Groups', '${stats['totalGroups']}'),
            _buildStatRow('Ungrouped', '${stats['ungroupedTabs']}'),
            _buildStatRow('Pinned', '${stats['pinnedTabs']}'),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12)),
          Text(
            value,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMainContent(BuildContext context, TabProvider tabProvider) {
    if (tabProvider.tabs.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.tab_unselected,
              size: 64,
              color: Theme.of(context).colorScheme.primary.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'No tabs yet',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text('Install browser extension to get started'),
          ],
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Groups
        if (tabProvider.groups.isNotEmpty) ...[
          Text(
            'Groups',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 16),
          ...tabProvider.groups.map((group) => _buildGroupCard(
                context,
                tabProvider,
                group,
              )),
          const SizedBox(height: 32),
        ],

        // All Tabs
        Text(
          'All Tabs',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        ...tabProvider.tabs.map((tab) => _buildTabCard(
              context,
              tabProvider,
              tab,
            )),
      ],
    );
  }

  Widget _buildGroupCard(
    BuildContext context,
    TabProvider tabProvider,
    TabGroup group,
  ) {
    final tabs = tabProvider.getTabsByGroup(group.id);

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ExpansionTile(
        leading: Icon(
          _getCategoryIcon(group.category),
          color: Color(int.parse('0x${group.colorHex}')),
        ),
        title: Text(group.name),
        subtitle: Text('${tabs.length} tabs'),
        children: tabs
            .map((tab) => _buildTabCard(context, tabProvider, tab, isInGroup: true))
            .toList(),
      ),
    );
  }

  Widget _buildTabCard(
    BuildContext context,
    TabProvider tabProvider,
    TabModel tab, {
    bool isInGroup = false,
  }) {
    return Card(
      margin: EdgeInsets.only(
        bottom: 8,
        left: isInGroup ? 16 : 0,
        right: isInGroup ? 16 : 0,
      ),
      child: ListTile(
        leading: tab.faviconUrl != null
            ? Image.network(
                tab.faviconUrl!,
                width: 24,
                height: 24,
                errorBuilder: (_, __, ___) => const Icon(Icons.public),
              )
            : const Icon(Icons.public),
        title: Text(
          tab.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          tab.url,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Chip(
              label: Text(
                tab.category,
                style: const TextStyle(fontSize: 10),
              ),
              backgroundColor: AppConstants.categoryColors[tab.category]
                  ?.withOpacity(0.2),
            ),
            IconButton(
              icon: const Icon(Icons.more_vert),
              onPressed: () => _showTabMenu(context, tabProvider, tab),
            ),
          ],
        ),
        onTap: () => tabProvider.selectTab(tab),
      ),
    );
  }

  Widget _buildFAB(BuildContext context) {
    return FloatingActionButton(
      onPressed: () => _showAddTabDialog(context),
      child: const Icon(Icons.add),
    );
  }

  void _showSearchDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Search Tabs'),
        content: TextField(
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'Enter search query...',
            prefixIcon: Icon(Icons.search),
          ),
          onChanged: (query) {
            context.read<TabProvider>().searchTabs(query);
          },
        ),
        actions: [
          TextButton(
            onPressed: () {
              context.read<TabProvider>().clearSearch();
              Navigator.pop(context);
            },
            child: const Text('Clear'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showSettingsDialog(BuildContext context) {
    // Settings dialog implementation
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Settings'),
        content: const Text('Settings screen coming soon...'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showAddTabDialog(BuildContext context) {
    final titleController = TextEditingController();
    final urlController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Tab'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleController,
              decoration: const InputDecoration(labelText: 'Title'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: urlController,
              decoration: const InputDecoration(labelText: 'URL'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<TabProvider>().addTab(
                    title: titleController.text,
                    url: urlController.text,
                    browser: 'manual',
                  );
              Navigator.pop(context);
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }

  void _showTabMenu(BuildContext context, TabProvider tabProvider, TabModel tab) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.delete),
            title: const Text('Delete'),
            onTap: () {
              tabProvider.deleteTab(tab.id);
              Navigator.pop(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.refresh),
            title: const Text('Reclassify'),
            onTap: () {
              // Reclassify tab
              Navigator.pop(context);
            },
          ),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'work':
        return Icons.work;
      case 'research':
        return Icons.school;
      case 'shopping':
        return Icons.shopping_cart;
      case 'social':
        return Icons.people;
      case 'entertainment':
        return Icons.movie;
      case 'news':
        return Icons.article;
      default:
        return Icons.category;
    }
  }

  String _capitalize(String text) {
    return text[0].toUpperCase() + text.substring(1);
  }
}
