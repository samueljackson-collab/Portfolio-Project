import 'package:flutter_test/flutter_test.dart';
import 'package:tab_organizer/models/tab.dart';

void main() {
  group('Tab Model', () {
    test('creates tab with required fields', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Example',
        createdAt: DateTime(2024, 1, 1),
      );

      expect(tab.id, '1');
      expect(tab.url, 'https://example.com');
      expect(tab.title, 'Example');
      expect(tab.createdAt, DateTime(2024, 1, 1));
    });

    test('creates tab with optional fields', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Example',
        description: 'Test description',
        faviconUrl: 'https://example.com/favicon.ico',
        createdAt: DateTime(2024, 1, 1),
        lastAccessed: DateTime(2024, 1, 2),
        visitCount: 5,
        groupId: 'group1',
        category: TabCategory.work,
        isHibernated: true,
        metadata: {'key': 'value'},
      );

      expect(tab.description, 'Test description');
      expect(tab.faviconUrl, 'https://example.com/favicon.ico');
      expect(tab.lastAccessed, DateTime(2024, 1, 2));
      expect(tab.visitCount, 5);
      expect(tab.groupId, 'group1');
      expect(tab.category, TabCategory.work);
      expect(tab.isHibernated, true);
      expect(tab.metadata, {'key': 'value'});
    });

    test('defaults visitCount to 1', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Example',
        createdAt: DateTime.now(),
      );

      expect(tab.visitCount, 1);
    });

    test('defaults isHibernated to false', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Example',
        createdAt: DateTime.now(),
      );

      expect(tab.isHibernated, false);
    });

    test('converts to and from JSON', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Example',
        description: 'Test',
        createdAt: DateTime(2024, 1, 1),
        category: TabCategory.work,
      );

      final json = tab.toJson();
      final restored = Tab.fromJson(json);

      expect(restored.id, tab.id);
      expect(restored.url, tab.url);
      expect(restored.title, tab.title);
      expect(restored.description, tab.description);
      expect(restored.category, tab.category);
    });

    test('copyWith creates new instance with updated fields', () {
      final original = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Original',
        createdAt: DateTime.now(),
      );

      final updated = original.copyWith(title: 'Updated');

      expect(updated.id, original.id);
      expect(updated.url, original.url);
      expect(updated.title, 'Updated');
      expect(updated.createdAt, original.createdAt);
    });
  });

  group('TabCategory', () {
    test('has all expected categories', () {
      expect(TabCategory.values.length, 9);
      expect(TabCategory.values, contains(TabCategory.work));
      expect(TabCategory.values, contains(TabCategory.research));
      expect(TabCategory.values, contains(TabCategory.shopping));
      expect(TabCategory.values, contains(TabCategory.socialMedia));
      expect(TabCategory.values, contains(TabCategory.entertainment));
      expect(TabCategory.values, contains(TabCategory.news));
      expect(TabCategory.values, contains(TabCategory.finance));
      expect(TabCategory.values, contains(TabCategory.education));
      expect(TabCategory.values, contains(TabCategory.other));
    });
  });

  group('TabCategoryExtension', () {
    test('displayName returns correct names', () {
      expect(TabCategory.work.displayName, 'Work');
      expect(TabCategory.research.displayName, 'Research');
      expect(TabCategory.shopping.displayName, 'Shopping');
      expect(TabCategory.socialMedia.displayName, 'Social Media');
      expect(TabCategory.entertainment.displayName, 'Entertainment');
      expect(TabCategory.news.displayName, 'News');
      expect(TabCategory.finance.displayName, 'Finance');
      expect(TabCategory.education.displayName, 'Education');
      expect(TabCategory.other.displayName, 'Other');
    });

    test('colorValue returns valid color codes', () {
      for (final category in TabCategory.values) {
        final color = category.colorValue;
        expect(color, isA<int>());
        expect(color, greaterThanOrEqualTo(0));
        // Verify it's a valid ARGB color (0xAARRGGBB)
        expect((color >> 24) & 0xFF, 0xFF); // Alpha channel should be FF
      }
    });

    test('each category has unique color', () {
      final colors = TabCategory.values.map((c) => c.colorValue).toSet();
      expect(colors.length, TabCategory.values.length);
    });

    test('specific color values are correct', () {
      expect(TabCategory.work.colorValue, 0xFF2196F3);
      expect(TabCategory.research.colorValue, 0xFF9C27B0);
      expect(TabCategory.shopping.colorValue, 0xFFFF9800);
      expect(TabCategory.socialMedia.colorValue, 0xFFE91E63);
      expect(TabCategory.entertainment.colorValue, 0xFFF44336);
      expect(TabCategory.news.colorValue, 0xFF4CAF50);
      expect(TabCategory.finance.colorValue, 0xFF00BCD4);
      expect(TabCategory.education.colorValue, 0xFF3F51B5);
      expect(TabCategory.other.colorValue, 0xFF9E9E9E);
    });
  });

  group('TabExtension', () {
    test('domain extracts domain from valid URL', () {
      final tab = Tab(
        id: '1',
        url: 'https://www.example.com/path/to/page?query=value',
        title: 'Example',
        createdAt: DateTime.now(),
      );

      expect(tab.domain, 'www.example.com');
    });

    test('domain handles URL without www', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com/page',
        title: 'Example',
        createdAt: DateTime.now(),
      );

      expect(tab.domain, 'example.com');
    });

    test('domain handles URL with port', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com:8080/page',
        title: 'Example',
        createdAt: DateTime.now(),
      );

      expect(tab.domain, 'example.com');
    });

    test('domain handles subdomain', () {
      final tab = Tab(
        id: '1',
        url: 'https://api.example.com/endpoint',
        title: 'API',
        createdAt: DateTime.now(),
      );

      expect(tab.domain, 'api.example.com');
    });

    test('domain returns empty string for invalid URL', () {
      final tab = Tab(
        id: '1',
        url: 'not-a-valid-url',
        title: 'Invalid',
        createdAt: DateTime.now(),
      );

      expect(tab.domain, '');
    });

    test('domain returns empty string for empty URL', () {
      final tab = Tab(
        id: '1',
        url: '',
        title: 'Empty',
        createdAt: DateTime.now(),
      );

      expect(tab.domain, '');
    });

    test('searchableText combines title, url, and description', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Example Title',
        description: 'Test Description',
        createdAt: DateTime.now(),
      );

      final searchable = tab.searchableText;
      expect(searchable, contains('example title'));
      expect(searchable, contains('https://example.com'));
      expect(searchable, contains('test description'));
    });

    test('searchableText is lowercase', () {
      final tab = Tab(
        id: '1',
        url: 'HTTPS://EXAMPLE.COM',
        title: 'UPPERCASE TITLE',
        description: 'UPPERCASE DESCRIPTION',
        createdAt: DateTime.now(),
      );

      final searchable = tab.searchableText;
      expect(searchable, equals(searchable.toLowerCase()));
      expect(searchable, isNot(contains('UPPERCASE')));
    });

    test('searchableText handles null description', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Example',
        createdAt: DateTime.now(),
      );

      expect(() => tab.searchableText, returnsNormally);
      final searchable = tab.searchableText;
      expect(searchable, contains('example'));
      expect(searchable, contains('https://example.com'));
    });

    test('searchableText is searchable', () {
      final tab = Tab(
        id: '1',
        url: 'https://github.com/flutter/flutter',
        title: 'Flutter Framework Repository',
        description: 'Open source UI framework',
        createdAt: DateTime.now(),
      );

      final searchable = tab.searchableText;
      expect(searchable.contains('flutter'), true);
      expect(searchable.contains('github'), true);
      expect(searchable.contains('framework'), true);
      expect(searchable.contains('open source'), true);
    });
  });

  group('Tab Edge Cases', () {
    test('handles very long URLs', () {
      final longUrl = 'https://example.com/' + 'a' * 10000;
      final tab = Tab(
        id: '1',
        url: longUrl,
        title: 'Long URL',
        createdAt: DateTime.now(),
      );

      expect(tab.url, longUrl);
      expect(tab.domain, 'example.com');
    });

    test('handles special characters in title', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Special <>&"\' Characters',
        createdAt: DateTime.now(),
      );

      expect(tab.title, 'Special <>&"\' Characters');
    });

    test('handles Unicode in URLs and titles', () {
      final tab = Tab(
        id: '1',
        url: 'https://例え.jp/パス',
        title: '日本語のタイトル',
        createdAt: DateTime.now(),
      );

      expect(tab.url, 'https://例え.jp/パス');
      expect(tab.title, '日本語のタイトル');
    });

    test('handles empty title', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: '',
        createdAt: DateTime.now(),
      );

      expect(tab.title, '');
      expect(tab.searchableText, isNotEmpty);
    });

    test('handles very old dates', () {
      final oldDate = DateTime(1970, 1, 1);
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Old',
        createdAt: oldDate,
      );

      expect(tab.createdAt, oldDate);
    });

    test('handles future dates', () {
      final futureDate = DateTime(2100, 12, 31);
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Future',
        createdAt: futureDate,
      );

      expect(tab.createdAt, futureDate);
    });

    test('handles negative visit count via copyWith', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Test',
        createdAt: DateTime.now(),
      ).copyWith(visitCount: -1);

      expect(tab.visitCount, -1);
    });

    test('handles extremely large visit count', () {
      final tab = Tab(
        id: '1',
        url: 'https://example.com',
        title: 'Test',
        createdAt: DateTime.now(),
        visitCount: 999999999,
      );

      expect(tab.visitCount, 999999999);
    });
  });
}