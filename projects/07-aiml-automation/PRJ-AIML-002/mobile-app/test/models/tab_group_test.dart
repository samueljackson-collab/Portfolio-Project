import 'package:flutter_test/flutter_test.dart';
import 'package:tab_organizer/models/tab.dart';
import 'package:tab_organizer/models/tab_group.dart';

void main() {
  group('TabGroup Model', () {
    test('creates tab group with required fields', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test Group',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2'],
        createdAt: DateTime(2024, 1, 1),
      );

      expect(group.id, 'group1');
      expect(group.name, 'Test Group');
      expect(group.category, TabCategory.work);
      expect(group.tabIds, ['tab1', 'tab2']);
      expect(group.createdAt, DateTime(2024, 1, 1));
    });

    test('creates tab group with optional fields', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test Group',
        category: TabCategory.work,
        tabIds: ['tab1'],
        createdAt: DateTime(2024, 1, 1),
        updatedAt: DateTime(2024, 1, 2),
        colorValue: 0xFF123456,
        isPinned: true,
        isCollapsed: true,
        metadata: {'key': 'value'},
      );

      expect(group.updatedAt, DateTime(2024, 1, 2));
      expect(group.colorValue, 0xFF123456);
      expect(group.isPinned, true);
      expect(group.isCollapsed, true);
      expect(group.metadata, {'key': 'value'});
    });

    test('defaults isPinned to false', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.isPinned, false);
    });

    test('defaults isCollapsed to false', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.isCollapsed, false);
    });

    test('converts to and from JSON', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test Group',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2', 'tab3'],
        createdAt: DateTime(2024, 1, 1),
        isPinned: true,
      );

      final json = group.toJson();
      final restored = TabGroup.fromJson(json);

      expect(restored.id, group.id);
      expect(restored.name, group.name);
      expect(restored.category, group.category);
      expect(restored.tabIds, group.tabIds);
      expect(restored.isPinned, group.isPinned);
    });

    test('copyWith creates new instance with updated fields', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Original',
        category: TabCategory.work,
        tabIds: ['tab1'],
        createdAt: DateTime.now(),
      );

      final updated = original.copyWith(name: 'Updated');

      expect(updated.id, original.id);
      expect(updated.name, 'Updated');
      expect(updated.category, original.category);
      expect(updated.tabIds, original.tabIds);
    });

    test('handles empty tab list', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Empty Group',
        category: TabCategory.other,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.tabIds, isEmpty);
    });
  });

  group('TabGroupExtension', () {
    test('color returns colorValue when set', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
        colorValue: 0xFF123456,
      );

      expect(group.color, 0xFF123456);
    });

    test('color returns category color when colorValue is null', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.color, TabCategory.work.colorValue);
    });

    test('tabCount returns correct count', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2', 'tab3'],
        createdAt: DateTime.now(),
      );

      expect(group.tabCount, 3);
    });

    test('tabCount returns 0 for empty group', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.tabCount, 0);
    });

    test('isEmpty returns true for empty group', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.isEmpty, true);
    });

    test('isEmpty returns false for non-empty group', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1'],
        createdAt: DateTime.now(),
      );

      expect(group.isEmpty, false);
    });

    test('addTab adds tab ID and updates timestamp', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1'],
        createdAt: DateTime(2024, 1, 1),
      );

      final updated = original.addTab('tab2');

      expect(updated.tabIds, ['tab1', 'tab2']);
      expect(updated.tabCount, 2);
      expect(updated.updatedAt, isNotNull);
      expect(updated.updatedAt!.isAfter(original.createdAt), true);
    });

    test('addTab preserves existing tabs', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2'],
        createdAt: DateTime.now(),
      );

      final updated = original.addTab('tab3');

      expect(updated.tabIds, ['tab1', 'tab2', 'tab3']);
    });

    test('addTab can add duplicate tab IDs', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1'],
        createdAt: DateTime.now(),
      );

      final updated = original.addTab('tab1');

      expect(updated.tabIds, ['tab1', 'tab1']);
      expect(updated.tabCount, 2);
    });

    test('removeTab removes tab ID and updates timestamp', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2', 'tab3'],
        createdAt: DateTime(2024, 1, 1),
      );

      final updated = original.removeTab('tab2');

      expect(updated.tabIds, ['tab1', 'tab3']);
      expect(updated.tabCount, 2);
      expect(updated.updatedAt, isNotNull);
      expect(updated.updatedAt!.isAfter(original.createdAt), true);
    });

    test('removeTab handles non-existent tab ID', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2'],
        createdAt: DateTime.now(),
      );

      final updated = original.removeTab('tab999');

      expect(updated.tabIds, ['tab1', 'tab2']);
      expect(updated.tabCount, 2);
    });

    test('removeTab can empty the group', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1'],
        createdAt: DateTime.now(),
      );

      final updated = original.removeTab('tab1');

      expect(updated.isEmpty, true);
      expect(updated.tabCount, 0);
    });

    test('removeTab removes all instances of duplicate tab IDs', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2', 'tab1', 'tab3'],
        createdAt: DateTime.now(),
      );

      final updated = original.removeTab('tab1');

      expect(updated.tabIds, ['tab2', 'tab3']);
      expect(updated.tabCount, 2);
    });

    test('rename updates name and timestamp', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Original Name',
        category: TabCategory.work,
        tabIds: ['tab1'],
        createdAt: DateTime(2024, 1, 1),
      );

      final updated = original.rename('New Name');

      expect(updated.name, 'New Name');
      expect(updated.updatedAt, isNotNull);
      expect(updated.updatedAt!.isAfter(original.createdAt), true);
    });

    test('rename preserves other fields', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Original',
        category: TabCategory.work,
        tabIds: ['tab1', 'tab2'],
        createdAt: DateTime.now(),
        isPinned: true,
        isCollapsed: true,
      );

      final updated = original.rename('New Name');

      expect(updated.id, original.id);
      expect(updated.category, original.category);
      expect(updated.tabIds, original.tabIds);
      expect(updated.isPinned, original.isPinned);
      expect(updated.isCollapsed, original.isCollapsed);
    });

    test('rename handles empty string', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Original',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      final updated = original.rename('');

      expect(updated.name, '');
    });

    test('rename handles special characters', () {
      final original = TabGroup(
        id: 'group1',
        name: 'Original',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      final updated = original.rename('Special <>&"\' Chars');

      expect(updated.name, 'Special <>&"\' Chars');
    });
  });

  group('TabGroup Edge Cases', () {
    test('handles very large number of tabs', () {
      final tabIds = List.generate(10000, (i) => 'tab$i');
      final group = TabGroup(
        id: 'group1',
        name: 'Large Group',
        category: TabCategory.work,
        tabIds: tabIds,
        createdAt: DateTime.now(),
      );

      expect(group.tabCount, 10000);
      expect(group.isEmpty, false);
    });

    test('handles very long group name', () {
      final longName = 'A' * 10000;
      final group = TabGroup(
        id: 'group1',
        name: longName,
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.name, longName);
    });

    test('handles Unicode in group name', () {
      final group = TabGroup(
        id: 'group1',
        name: '日本語のグループ名 🚀',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      expect(group.name, '日本語のグループ名 🚀');
    });

    test('multiple operations maintain consistency', () {
      var group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      );

      group = group.addTab('tab1');
      group = group.addTab('tab2');
      group = group.addTab('tab3');
      expect(group.tabCount, 3);

      group = group.removeTab('tab2');
      expect(group.tabCount, 2);
      expect(group.tabIds, ['tab1', 'tab3']);

      group = group.rename('Updated');
      expect(group.name, 'Updated');
      expect(group.tabCount, 2);
    });

    test('chain operations work correctly', () {
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
      ).addTab('tab1').addTab('tab2').removeTab('tab1').rename('Final');

      expect(group.name, 'Final');
      expect(group.tabIds, ['tab2']);
    });
  });

  group('TabGroup Color Logic', () {
    test('each category has default color', () {
      for (final category in TabCategory.values) {
        final group = TabGroup(
          id: 'group1',
          name: 'Test',
          category: category,
          tabIds: [],
          createdAt: DateTime.now(),
        );

        expect(group.color, category.colorValue);
      }
    });

    test('custom color overrides category color', () {
      final customColor = 0xFFABCDEF;
      final group = TabGroup(
        id: 'group1',
        name: 'Test',
        category: TabCategory.work,
        tabIds: [],
        createdAt: DateTime.now(),
        colorValue: customColor,
      );

      expect(group.color, customColor);
      expect(group.color, isNot(equals(TabCategory.work.colorValue)));
    });
  });
}