import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:hive/hive.dart';
import 'package:tab_organizer/services/tab_service.dart';
import 'package:tab_organizer/models/tab_model.dart';

@GenerateMocks([Box])
import 'tab_service_test.mocks.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('TabService', () {
    late TabService tabService;
    late MockBox<TabModel> mockTabsBox;
    late MockBox<TabGroup> mockGroupsBox;

    setUp(() {
      tabService = TabService();
      mockTabsBox = MockBox<TabModel>();
      mockGroupsBox = MockBox<TabGroup>();
    });

    group('Tab Management', () {
      test('addTab creates a new tab with UUID', () async {
        when(mockTabsBox.put(any, any)).thenAnswer((_) async => null);
        
        // Mock the box initialization
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final tab = await tabService.addTab(
          title: 'Test Tab',
          url: 'https://example.com',
          category: 'work',
          browser: 'chrome',
        );

        expect(tab.id, isNotEmpty);
        expect(tab.title, 'Test Tab');
        expect(tab.url, 'https://example.com');
        expect(tab.category, 'work');
        expect(tab.browser, 'chrome');
        verify(mockTabsBox.put(any, any)).called(1);
      });

      test('addTab extracts domain from URL', () async {
        when(mockTabsBox.put(any, any)).thenAnswer((_) async => null);
        
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final tab = await tabService.addTab(
          title: 'Test',
          url: 'https://github.com/user/repo',
          category: 'work',
          browser: 'chrome',
        );

        expect(tab.domain, 'github.com');
      });

      test('getAllTabs returns all tabs', () {
        final tabs = [
          TabModel(
            id: '1',
            title: 'Tab 1',
            url: 'https://example.com/1',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 0,
          ),
          TabModel(
            id: '2',
            title: 'Tab 2',
            url: 'https://example.com/2',
            category: 'social',
            confidenceScore: 0.9,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'firefox',
            tabIndex: 1,
          ),
        ];

        when(mockTabsBox.values).thenReturn(tabs);
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final result = tabService.getAllTabs();

        expect(result.length, 2);
        expect(result[0].title, 'Tab 1');
        expect(result[1].title, 'Tab 2');
      });

      test('getTabsByCategory filters tabs correctly', () {
        final tabs = [
          TabModel(
            id: '1',
            title: 'Work Tab',
            url: 'https://github.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 0,
          ),
          TabModel(
            id: '2',
            title: 'Social Tab',
            url: 'https://facebook.com',
            category: 'social',
            confidenceScore: 0.9,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 1,
          ),
          TabModel(
            id: '3',
            title: 'Another Work Tab',
            url: 'https://gitlab.com',
            category: 'work',
            confidenceScore: 0.85,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 2,
          ),
        ];

        when(mockTabsBox.values).thenReturn(tabs);
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final workTabs = tabService.getTabsByCategory('work');

        expect(workTabs.length, 2);
        expect(workTabs.every((t) => t.category == 'work'), true);
      });

      test('searchTabs finds matching tabs', () {
        final tabs = [
          TabModel(
            id: '1',
            title: 'GitHub Repository',
            url: 'https://github.com/user/repo',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 0,
          ),
          TabModel(
            id: '2',
            title: 'Facebook Profile',
            url: 'https://facebook.com/profile',
            category: 'social',
            confidenceScore: 0.9,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 1,
          ),
        ];

        when(mockTabsBox.values).thenReturn(tabs);
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final results = tabService.searchTabs('github');

        expect(results.length, 1);
        expect(results[0].title, 'GitHub Repository');
      });

      test('searchTabs is case-insensitive', () {
        final tabs = [
          TabModel(
            id: '1',
            title: 'GitHub Repository',
            url: 'https://github.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 0,
          ),
        ];

        when(mockTabsBox.values).thenReturn(tabs);
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final results = tabService.searchTabs('GITHUB');

        expect(results.length, 1);
      });

      test('deleteTab removes tab', () async {
        when(mockTabsBox.delete(any)).thenAnswer((_) async => null);
        
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        await tabService.deleteTab('tab-123');

        verify(mockTabsBox.delete('tab-123')).called(1);
      });
    });

    group('Duplicate Detection', () {
      test('findDuplicates identifies duplicate URLs', () {
        final tabs = [
          TabModel(
            id: '1',
            title: 'Tab 1',
            url: 'https://example.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime(2024, 1, 1, 10, 0),
            lastAccessed: DateTime(2024, 1, 1, 10, 0),
            browser: 'chrome',
            tabIndex: 0,
          ),
          TabModel(
            id: '2',
            title: 'Tab 2',
            url: 'https://example.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime(2024, 1, 1, 11, 0),
            lastAccessed: DateTime(2024, 1, 1, 11, 0),
            browser: 'chrome',
            tabIndex: 1,
          ),
          TabModel(
            id: '3',
            title: 'Tab 3',
            url: 'https://different.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime(2024, 1, 1, 12, 0),
            lastAccessed: DateTime(2024, 1, 1, 12, 0),
            browser: 'chrome',
            tabIndex: 2,
          ),
        ];

        when(mockTabsBox.values).thenReturn(tabs);
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final duplicates = tabService.findDuplicates();

        expect(duplicates.length, 1);
        expect(duplicates[0].length, 2);
      });

      test('findDuplicates returns empty for no duplicates', () {
        final tabs = [
          TabModel(
            id: '1',
            title: 'Tab 1',
            url: 'https://example1.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 0,
          ),
          TabModel(
            id: '2',
            title: 'Tab 2',
            url: 'https://example2.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 1,
          ),
        ];

        when(mockTabsBox.values).thenReturn(tabs);
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final duplicates = tabService.findDuplicates();

        expect(duplicates, isEmpty);
      });
    });

    group('Group Management', () {
      test('createGroup creates a new group', () async {
        when(mockGroupsBox.put(any, any)).thenAnswer((_) async => null);
        when(mockGroupsBox.length).thenReturn(0);
        
        tabService._groupsBox = mockGroupsBox;
        tabService._isInitialized = true;

        final group = await tabService.createGroup(
          name: 'Work Tabs',
          category: 'work',
        );

        expect(group.id, isNotEmpty);
        expect(group.name, 'Work Tabs');
        expect(group.category, 'work');
        verify(mockGroupsBox.put(any, any)).called(1);
      });

      test('getAllGroups returns sorted groups', () {
        final groups = [
          TabGroup(
            id: 'group-2',
            name: 'Group 2',
            category: 'work',
            tabIds: [],
            colorHex: '#000000',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
            sortOrder: 2,
          ),
          TabGroup(
            id: 'group-1',
            name: 'Group 1',
            category: 'work',
            tabIds: [],
            colorHex: '#000000',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
            sortOrder: 1,
          ),
        ];

        when(mockGroupsBox.values).thenReturn(groups);
        tabService._groupsBox = mockGroupsBox;
        tabService._isInitialized = true;

        final result = tabService.getAllGroups();

        expect(result.length, 2);
        expect(result[0].sortOrder, 1);
        expect(result[1].sortOrder, 2);
      });

      test('addTabToGroup updates both tab and group', () async {
        final tab = TabModel(
          id: 'tab-1',
          title: 'Test Tab',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
        );

        final group = TabGroup(
          id: 'group-1',
          name: 'Work Group',
          category: 'work',
          tabIds: [],
          colorHex: '#000000',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        when(mockTabsBox.get('tab-1')).thenReturn(tab);
        when(mockGroupsBox.get('group-1')).thenReturn(group);
        when(mockTabsBox.put(any, any)).thenAnswer((_) async => null);
        when(mockGroupsBox.put(any, any)).thenAnswer((_) async => null);

        tabService._tabsBox = mockTabsBox;
        tabService._groupsBox = mockGroupsBox;
        tabService._isInitialized = true;

        await tabService.addTabToGroup('tab-1', 'group-1');

        verify(mockTabsBox.put(any, any)).called(1);
        verify(mockGroupsBox.put(any, any)).called(1);
      });
    });

    group('Import/Export', () {
      test('exportTabs creates valid export data', () {
        final tabs = [
          TabModel(
            id: '1',
            title: 'Tab 1',
            url: 'https://example.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 0,
          ),
        ];

        final groups = [
          TabGroup(
            id: 'group-1',
            name: 'Group 1',
            category: 'work',
            tabIds: ['1'],
            colorHex: '#000000',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ),
        ];

        when(mockTabsBox.values).thenReturn(tabs);
        when(mockGroupsBox.values).thenReturn(groups);
        
        tabService._tabsBox = mockTabsBox;
        tabService._groupsBox = mockGroupsBox;
        tabService._isInitialized = true;

        final exportData = tabService.exportTabs();

        expect(exportData['tabs'], isA<List>());
        expect(exportData['groups'], isA<List>());
        expect(exportData['exportedAt'], isNotEmpty);
        expect(exportData['version'], isNotEmpty);
      });
    });

    group('Edge Cases', () {
      test('getAllTabs returns empty list when not initialized', () {
        final result = tabService.getAllTabs();
        expect(result, isEmpty);
      });

      test('searchTabs returns empty for empty query', () {
        when(mockTabsBox.values).thenReturn([]);
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final results = tabService.searchTabs('');
        expect(results, isEmpty);
      });

      test('extractDomain handles invalid URLs', () {
        when(mockTabsBox.put(any, any)).thenAnswer((_) async => null);
        
        tabService._tabsBox = mockTabsBox;
        tabService._isInitialized = true;

        final tab = await tabService.addTab(
          title: 'Test',
          url: 'invalid-url',
          category: 'work',
          browser: 'chrome',
        );

        expect(tab.domain, '');
      });
    });
  });
}