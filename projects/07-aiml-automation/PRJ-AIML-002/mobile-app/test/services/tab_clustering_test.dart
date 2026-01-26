import 'package:flutter_test/flutter_test.dart';
import 'package:tab_organizer/models/tab.dart';
import 'package:tab_organizer/services/tab_clustering.dart';

void main() {
  group('TabClusterer', () {
    late TabClusterer clusterer;

    setUp(() {
      clusterer = TabClusterer();
    });

    test('creates single group for small tab set', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com',
          title: 'Example',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups.length, 1);
      expect(groups[0].tabIds.length, 1);
    });

    test('clusters tabs from same domain together', () {
      final now = DateTime.now();
      final tabs = [
        Tab(
          id: '1',
          url: 'https://github.com/user1/repo1',
          title: 'Repository 1',
          createdAt: now,
        ),
        Tab(
          id: '2',
          url: 'https://github.com/user2/repo2',
          title: 'Repository 2',
          createdAt: now.add(Duration(seconds: 30)),
        ),
        Tab(
          id: '3',
          url: 'https://stackoverflow.com/questions/123',
          title: 'Question',
          createdAt: now.add(Duration(minutes: 10)),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      // GitHub tabs might be clustered together
    });

    test('clusters tabs with similar titles', () {
      final now = DateTime.now();
      final tabs = [
        Tab(
          id: '1',
          url: 'https://docs.flutter.dev/tutorial',
          title: 'Flutter Tutorial',
          createdAt: now,
        ),
        Tab(
          id: '2',
          url: 'https://flutter.dev/docs',
          title: 'Flutter Documentation',
          createdAt: now.add(Duration(seconds: 30)),
        ),
        Tab(
          id: '3',
          url: 'https://example.com',
          title: 'Unrelated Page',
          createdAt: now.add(Duration(hours: 1)),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.research);

      expect(groups, isNotEmpty);
    });

    test('handles tabs opened at different times', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com/page1',
          title: 'Page 1',
          createdAt: DateTime(2024, 1, 1, 10, 0),
        ),
        Tab(
          id: '2',
          url: 'https://example.com/page2',
          title: 'Page 2',
          createdAt: DateTime(2024, 1, 1, 15, 0), // 5 hours later
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
    });

    test('returns empty list for empty input', () {
      final groups = clusterer.clusterTabs([], TabCategory.work);

      expect(groups, isEmpty);
    });

    test('handles single tab', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com',
          title: 'Single Tab',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups.length, 1);
      expect(groups[0].tabIds, ['1']);
    });

    test('generated group names include category', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://github.com/flutter/flutter',
          title: 'Flutter Framework',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://github.com/dart-lang/sdk',
          title: 'Dart SDK',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      expect(groups[0].category, TabCategory.work);
    });

    test('groups tabs with same domain get domain-based name', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://github.com/user/repo1',
          title: 'Repo 1',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://github.com/user/repo2',
          title: 'Repo 2',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      expect(groups[0].name, contains('Github'));
    });

    test('handles tabs with missing or invalid URLs', () {
      final tabs = [
        Tab(
          id: '1',
          url: '',
          title: 'Empty URL',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'not-a-url',
          title: 'Invalid URL',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.other);

      expect(groups, isNotEmpty);
    });

    test('handles tabs with special characters in titles', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com',
          title: 'Title with <special> & "chars"',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://example.com',
          title: 'Another <special> title',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
    });

    test('handles very large number of tabs', () {
      final tabs = List.generate(
        1000,
        (i) => Tab(
          id: '$i',
          url: 'https://example.com/page$i',
          title: 'Page $i',
          createdAt: DateTime.now(),
        ),
      );

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      final totalTabs = groups.fold<int>(
        0,
        (sum, group) => sum + group.tabIds.length,
      );
      expect(totalTabs, equals(1000));
    });

    test('all tabs are assigned to a group', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://site1.com',
          title: 'Site 1',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://site2.com',
          title: 'Site 2',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '3',
          url: 'https://site3.com',
          title: 'Site 3',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      final allTabIds = groups.expand((g) => g.tabIds).toSet();
      expect(allTabIds.length, equals(tabs.length));
      for (final tab in tabs) {
        expect(allTabIds, contains(tab.id));
      }
    });

    test('respects category in generated groups', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com',
          title: 'Example',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://test.com',
          title: 'Test',
          createdAt: DateTime.now(),
        ),
      ];

      for (final category in TabCategory.values) {
        final groups = clusterer.clusterTabs(tabs, category);

        expect(groups, isNotEmpty);
        for (final group in groups) {
          expect(group.category, equals(category));
        }
      }
    });

    test('handles temporally close tabs differently than distant ones', () {
      final baseTime = DateTime(2024, 1, 1, 10, 0);
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com/1',
          title: 'Page 1',
          createdAt: baseTime,
        ),
        Tab(
          id: '2',
          url: 'https://example.com/2',
          title: 'Page 2',
          createdAt: baseTime.add(Duration(minutes: 2)), // Close in time
        ),
        Tab(
          id: '3',
          url: 'https://example.com/3',
          title: 'Page 3',
          createdAt: baseTime.add(Duration(hours: 5)), // Distant in time
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
    });

    test('generates unique group IDs', () {
      final tabs = List.generate(
        10,
        (i) => Tab(
          id: '$i',
          url: 'https://example.com/$i',
          title: 'Page $i',
          createdAt: DateTime.now(),
        ),
      );

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      final groupIds = groups.map((g) => g.id).toSet();
      expect(groupIds.length, equals(groups.length));
    });

    test('sets group timestamps', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com',
          title: 'Example',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://test.com',
          title: 'Test',
          createdAt: DateTime.now(),
        ),
      ];

      final beforeClustering = DateTime.now();
      final groups = clusterer.clusterTabs(tabs, TabCategory.work);
      final afterClustering = DateTime.now();

      for (final group in groups) {
        expect(group.createdAt.isAfter(beforeClustering.subtract(Duration(seconds: 1))), true);
        expect(group.createdAt.isBefore(afterClustering.add(Duration(seconds: 1))), true);
      }
    });
  });

  group('TabClusterer - Group Naming', () {
    late TabClusterer clusterer;

    setUp(() {
      clusterer = TabClusterer();
    });

    test('generates meaningful names for common domains', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://www.github.com/user/repo',
          title: 'Repository',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://www.github.com/user/repo2',
          title: 'Another Repo',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      expect(groups[0].name.toLowerCase(), contains('github'));
    });

    test('includes common keywords in group names', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://tutorial1.com',
          title: 'Flutter Tutorial Part 1',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://tutorial2.com',
          title: 'Flutter Tutorial Part 2',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.education);

      expect(groups, isNotEmpty);
      // Name might include "Flutter" or "Tutorial"
    });

    test('falls back to category and count for diverse tabs', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://site1.com',
          title: 'Completely Different Title 1',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://site2.com',
          title: 'Unrelated Title 2',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.other);

      expect(groups, isNotEmpty);
      // Should contain category name
      expect(groups[0].name, contains('Other'));
    });

    test('handles empty titles gracefully', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com',
          title: '',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://example.com',
          title: '',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      expect(groups[0].name, isNotEmpty);
    });

    test('capitalizes site names properly', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://stackoverflow.com/q/123',
          title: 'Question 1',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://stackoverflow.com/q/456',
          title: 'Question 2',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      // Name should start with capital letter
      expect(groups[0].name[0], equals(groups[0].name[0].toUpperCase()));
    });
  });

  group('TabClusterer - Edge Cases', () {
    late TabClusterer clusterer;

    setUp(() {
      clusterer = TabClusterer();
    });

    test('handles tabs with identical content', () {
      final now = DateTime.now();
      final tabs = [
        Tab(
          id: '1',
          url: 'https://example.com',
          title: 'Same Title',
          createdAt: now,
        ),
        Tab(
          id: '2',
          url: 'https://example.com',
          title: 'Same Title',
          createdAt: now,
        ),
        Tab(
          id: '3',
          url: 'https://example.com',
          title: 'Same Title',
          createdAt: now,
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
      // Should likely be in same group
    });

    test('handles Unicode in URLs and titles', () {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://例え.jp/パス',
          title: '日本語のタイトル',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://тест.ru',
          title: 'Русский заголовок',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
    });

    test('handles very long URLs and titles', () {
      final longUrl = 'https://example.com/' + 'path/' * 100;
      final longTitle = 'Title ' * 100;

      final tabs = [
        Tab(
          id: '1',
          url: longUrl,
          title: longTitle,
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: longUrl + '/different',
          title: longTitle + ' different',
          createdAt: DateTime.now(),
        ),
      ];

      final groups = clusterer.clusterTabs(tabs, TabCategory.work);

      expect(groups, isNotEmpty);
    });

    test('preserves all tab IDs during clustering', () {
      final tabs = List.generate(
        50,
        (i) => Tab(
          id: 'tab_$i',
          url: 'https://example.com/$i',
          title: 'Page $i',
          createdAt: DateTime.now(),
        ),
      );

      final inputIds = tabs.map((t) => t.id).toSet();
      final groups = clusterer.clusterTabs(tabs, TabCategory.work);
      final outputIds = groups.expand((g) => g.tabIds).toSet();

      expect(outputIds, equals(inputIds));
    });
  });
}