import 'package:flutter_test/flutter_test.dart';
import 'package:tab_organizer/models/tab.dart';
import 'package:tab_organizer/services/tab_classifier.dart';

void main() {
  group('TabClassifier', () {
    late TabClassifier classifier;

    setUp(() {
      classifier = TabClassifier.instance;
    });

    test('classifies work-related tabs correctly', () async {
      final tab = Tab(
        id: '1',
        url: 'https://linkedin.com/in/profile',
        title: 'LinkedIn Profile - Professional Network',
        createdAt: DateTime.now(),
      );

      final result = await classifier.classifyTab(tab);

      expect(result.category, TabCategory.work);
      expect(result.confidence, greaterThan(0.7));
    });

    test('classifies research tabs correctly', () async {
      final tab = Tab(
        id: '2',
        url: 'https://wikipedia.org/wiki/Artificial_Intelligence',
        title: 'Artificial Intelligence - Wikipedia',
        description: 'Encyclopedia article about AI',
        createdAt: DateTime.now(),
      );

      final result = await classifier.classifyTab(tab);

      expect(result.category, TabCategory.research);
    });

    test('classifies shopping tabs correctly', () async {
      final tab = Tab(
        id: '3',
        url: 'https://amazon.com/product/12345',
        title: 'Buy Product - Amazon',
        createdAt: DateTime.now(),
      );

      final result = await classifier.classifyTab(tab);

      expect(result.category, TabCategory.shopping);
    });

    test('handles batch classification', () async {
      final tabs = [
        Tab(
          id: '1',
          url: 'https://linkedin.com',
          title: 'LinkedIn',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '2',
          url: 'https://github.com',
          title: 'GitHub',
          createdAt: DateTime.now(),
        ),
        Tab(
          id: '3',
          url: 'https://stackoverflow.com',
          title: 'Stack Overflow',
          createdAt: DateTime.now(),
        ),
      ];

      final results = await classifier.classifyBatch(tabs);

      expect(results.length, tabs.length);
      for (final result in results) {
        expect(result.category, isNotNull);
        expect(result.confidence, greaterThanOrEqualTo(0.0));
        expect(result.confidence, lessThanOrEqualTo(1.0));
      }
    });

    test('returns fallback for invalid tabs', () async {
      final tab = Tab(
        id: '999',
        url: '',
        title: '',
        createdAt: DateTime.now(),
      );

      final result = await classifier.classifyTab(tab);

      expect(result.category, TabCategory.other);
    });
  });
}
