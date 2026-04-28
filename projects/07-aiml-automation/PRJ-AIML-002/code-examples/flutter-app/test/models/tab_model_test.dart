import 'package:flutter_test/flutter_test.dart';
import 'package:tab_organizer/models/tab_model.dart';

void main() {
  group('TabModel', () {
    late DateTime testCreatedAt;
    late DateTime testLastAccessed;

    setUp(() {
      testCreatedAt = DateTime(2024, 1, 1, 12, 0);
      testLastAccessed = DateTime(2024, 1, 1, 12, 30);
    });

    group('Construction', () {
      test('creates TabModel with required fields', () {
        final tab = TabModel(
          id: '123',
          title: 'Test Tab',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.85,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          browser: 'chrome',
          tabIndex: 0,
        );

        expect(tab.id, '123');
        expect(tab.title, 'Test Tab');
        expect(tab.url, 'https://example.com');
        expect(tab.category, 'work');
        expect(tab.confidenceScore, 0.85);
        expect(tab.browser, 'chrome');
        expect(tab.tabIndex, 0);
      });

      test('creates TabModel with optional fields', () {
        final tab = TabModel(
          id: '123',
          title: 'Test Tab',
          url: 'https://example.com',
          faviconUrl: 'https://example.com/favicon.ico',
          category: 'work',
          confidenceScore: 0.85,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          groupId: 'group-1',
          browser: 'chrome',
          tabIndex: 5,
          isPinned: true,
          isActive: true,
          domain: 'example.com',
          metadata: {'key': 'value'},
        );

        expect(tab.faviconUrl, 'https://example.com/favicon.ico');
        expect(tab.groupId, 'group-1');
        expect(tab.isPinned, true);
        expect(tab.isActive, true);
        expect(tab.domain, 'example.com');
        expect(tab.metadata?['key'], 'value');
      });

      test('defaults isPinned and isActive to false', () {
        final tab = TabModel(
          id: '123',
          title: 'Test',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          browser: 'chrome',
          tabIndex: 0,
        );

        expect(tab.isPinned, false);
        expect(tab.isActive, false);
      });
    });

    group('JSON Serialization', () {
      test('converts TabModel to JSON', () {
        final tab = TabModel(
          id: '123',
          title: 'Test Tab',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.85,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          browser: 'chrome',
          tabIndex: 0,
        );

        final json = tab.toJson();

        expect(json['id'], '123');
        expect(json['title'], 'Test Tab');
        expect(json['url'], 'https://example.com');
        expect(json['category'], 'work');
        expect(json['confidenceScore'], 0.85);
        expect(json['browser'], 'chrome');
      });

      test('creates TabModel from JSON', () {
        final json = {
          'id': '123',
          'title': 'Test Tab',
          'url': 'https://example.com',
          'category': 'work',
          'confidenceScore': 0.85,
          'createdAt': testCreatedAt.toIso8601String(),
          'lastAccessed': testLastAccessed.toIso8601String(),
          'browser': 'chrome',
          'tabIndex': 0,
          'isPinned': false,
          'isActive': false,
        };

        final tab = TabModel.fromJson(json);

        expect(tab.id, '123');
        expect(tab.title, 'Test Tab');
        expect(tab.url, 'https://example.com');
        expect(tab.category, 'work');
        expect(tab.confidenceScore, 0.85);
      });

      test('handles null optional fields in JSON', () {
        final json = {
          'id': '123',
          'title': 'Test',
          'url': 'https://example.com',
          'category': 'work',
          'confidenceScore': 0.8,
          'createdAt': testCreatedAt.toIso8601String(),
          'lastAccessed': testLastAccessed.toIso8601String(),
          'browser': 'chrome',
          'tabIndex': 0,
          'faviconUrl': null,
          'groupId': null,
          'domain': null,
          'metadata': null,
        };

        final tab = TabModel.fromJson(json);

        expect(tab.faviconUrl, isNull);
        expect(tab.groupId, isNull);
        expect(tab.domain, isNull);
        expect(tab.metadata, isNull);
      });
    });

    group('copyWith', () {
      test('creates copy with updated title', () {
        final original = TabModel(
          id: '123',
          title: 'Original',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          browser: 'chrome',
          tabIndex: 0,
        );

        final copy = original.copyWith(title: 'Updated');

        expect(copy.id, '123');
        expect(copy.title, 'Updated');
        expect(copy.url, 'https://example.com');
      });

      test('creates copy with multiple updated fields', () {
        final original = TabModel(
          id: '123',
          title: 'Original',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          browser: 'chrome',
          tabIndex: 0,
        );

        final copy = original.copyWith(
          title: 'Updated',
          category: 'research',
          isPinned: true,
          groupId: 'group-1',
        );

        expect(copy.title, 'Updated');
        expect(copy.category, 'research');
        expect(copy.isPinned, true);
        expect(copy.groupId, 'group-1');
        expect(copy.id, '123'); // Unchanged fields remain the same
      });

      test('returns same values when no parameters provided', () {
        final original = TabModel(
          id: '123',
          title: 'Original',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          browser: 'chrome',
          tabIndex: 0,
        );

        final copy = original.copyWith();

        expect(copy.id, original.id);
        expect(copy.title, original.title);
        expect(copy.url, original.url);
      });
    });

    group('toString', () {
      test('returns string representation', () {
        final tab = TabModel(
          id: '123',
          title: 'Test Tab',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.85,
          createdAt: testCreatedAt,
          lastAccessed: testLastAccessed,
          browser: 'chrome',
          tabIndex: 0,
        );

        final str = tab.toString();

        expect(str, contains('123'));
        expect(str, contains('Test Tab'));
        expect(str, contains('https://example.com'));
        expect(str, contains('work'));
      });
    });
  });

  group('TabGroup', () {
    late DateTime testCreatedAt;
    late DateTime testUpdatedAt;

    setUp(() {
      testCreatedAt = DateTime(2024, 1, 1, 12, 0);
      testUpdatedAt = DateTime(2024, 1, 1, 13, 0);
    });

    group('Construction', () {
      test('creates TabGroup with required fields', () {
        final group = TabGroup(
          id: 'group-1',
          name: 'Work Tabs',
          category: 'work',
          tabIds: ['tab-1', 'tab-2'],
          colorHex: '#3B82F6',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        expect(group.id, 'group-1');
        expect(group.name, 'Work Tabs');
        expect(group.category, 'work');
        expect(group.tabIds, ['tab-1', 'tab-2']);
        expect(group.colorHex, '#3B82F6');
      });

      test('defaults isCollapsed to false and sortOrder to 0', () {
        final group = TabGroup(
          id: 'group-1',
          name: 'Test',
          category: 'work',
          tabIds: [],
          colorHex: '#000000',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        expect(group.isCollapsed, false);
        expect(group.sortOrder, 0);
      });

      test('creates TabGroup with custom sortOrder', () {
        final group = TabGroup(
          id: 'group-1',
          name: 'Test',
          category: 'work',
          tabIds: [],
          colorHex: '#000000',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
          sortOrder: 5,
        );

        expect(group.sortOrder, 5);
      });
    });

    group('tabCount getter', () {
      test('returns correct tab count', () {
        final group = TabGroup(
          id: 'group-1',
          name: 'Test',
          category: 'work',
          tabIds: ['tab-1', 'tab-2', 'tab-3'],
          colorHex: '#000000',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        expect(group.tabCount, 3);
      });

      test('returns 0 for empty group', () {
        final group = TabGroup(
          id: 'group-1',
          name: 'Empty',
          category: 'work',
          tabIds: [],
          colorHex: '#000000',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        expect(group.tabCount, 0);
      });
    });

    group('JSON Serialization', () {
      test('converts TabGroup to JSON', () {
        final group = TabGroup(
          id: 'group-1',
          name: 'Work Tabs',
          category: 'work',
          tabIds: ['tab-1', 'tab-2'],
          colorHex: '#3B82F6',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        final json = group.toJson();

        expect(json['id'], 'group-1');
        expect(json['name'], 'Work Tabs');
        expect(json['category'], 'work');
        expect(json['tabIds'], ['tab-1', 'tab-2']);
      });

      test('creates TabGroup from JSON', () {
        final json = {
          'id': 'group-1',
          'name': 'Work Tabs',
          'category': 'work',
          'tabIds': ['tab-1', 'tab-2'],
          'colorHex': '#3B82F6',
          'createdAt': testCreatedAt.toIso8601String(),
          'updatedAt': testUpdatedAt.toIso8601String(),
          'isCollapsed': false,
          'sortOrder': 0,
        };

        final group = TabGroup.fromJson(json);

        expect(group.id, 'group-1');
        expect(group.name, 'Work Tabs');
        expect(group.tabIds.length, 2);
      });
    });

    group('copyWith', () {
      test('creates copy with updated name', () {
        final original = TabGroup(
          id: 'group-1',
          name: 'Original',
          category: 'work',
          tabIds: ['tab-1'],
          colorHex: '#000000',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        final copy = original.copyWith(name: 'Updated');

        expect(copy.name, 'Updated');
        expect(copy.id, 'group-1');
      });

      test('creates copy with updated tabIds', () {
        final original = TabGroup(
          id: 'group-1',
          name: 'Test',
          category: 'work',
          tabIds: ['tab-1'],
          colorHex: '#000000',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        final copy = original.copyWith(tabIds: ['tab-1', 'tab-2', 'tab-3']);

        expect(copy.tabIds.length, 3);
        expect(copy.tabCount, 3);
      });
    });

    group('toString', () {
      test('returns string representation', () {
        final group = TabGroup(
          id: 'group-1',
          name: 'Work Tabs',
          category: 'work',
          tabIds: ['tab-1', 'tab-2'],
          colorHex: '#3B82F6',
          createdAt: testCreatedAt,
          updatedAt: testUpdatedAt,
        );

        final str = group.toString();

        expect(str, contains('group-1'));
        expect(str, contains('Work Tabs'));
        expect(str, contains('work'));
        expect(str, contains('2')); // tabCount
      });
    });
  });

  group('Edge Cases', () {
    test('TabModel handles very long URLs', () {
      final longUrl = 'https://example.com/' + ('a' * 1000);
      final tab = TabModel(
        id: '123',
        title: 'Test',
        url: longUrl,
        category: 'work',
        confidenceScore: 0.8,
        createdAt: DateTime.now(),
        lastAccessed: DateTime.now(),
        browser: 'chrome',
        tabIndex: 0,
      );

      expect(tab.url.length, greaterThan(1000));
    });

    test('TabModel handles special characters in title', () {
      final tab = TabModel(
        id: '123',
        title: 'Test 测试 🎉 @#\$%',
        url: 'https://example.com',
        category: 'work',
        confidenceScore: 0.8,
        createdAt: DateTime.now(),
        lastAccessed: DateTime.now(),
        browser: 'chrome',
        tabIndex: 0,
      );

      expect(tab.title, 'Test 测试 🎉 @#\$%');
    });

    test('TabGroup handles empty tabIds list', () {
      final group = TabGroup(
        id: 'group-1',
        name: 'Empty Group',
        category: 'work',
        tabIds: [],
        colorHex: '#000000',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(group.tabCount, 0);
      expect(group.tabIds, isEmpty);
    });

    test('TabModel handles negative confidence score', () {
      final tab = TabModel(
        id: '123',
        title: 'Test',
        url: 'https://example.com',
        category: 'work',
        confidenceScore: -0.5,
        createdAt: DateTime.now(),
        lastAccessed: DateTime.now(),
        browser: 'chrome',
        tabIndex: 0,
      );

      expect(tab.confidenceScore, -0.5);
    });

    test('TabModel handles confidence score above 1.0', () {
      final tab = TabModel(
        id: '123',
        title: 'Test',
        url: 'https://example.com',
        category: 'work',
        confidenceScore: 1.5,
        createdAt: DateTime.now(),
        lastAccessed: DateTime.now(),
        browser: 'chrome',
        tabIndex: 0,
      );

      expect(tab.confidenceScore, 1.5);
    });
  });
}