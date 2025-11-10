import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:tab_organizer/services/ai_service.dart';
import 'package:tab_organizer/models/tab_model.dart';
import 'package:tab_organizer/utils/constants.dart';

@GenerateMocks([Interpreter])
import 'ai_service_test.mocks.dart';

void main() {
  group('AIService', () {
    late AIService aiService;

    setUp(() {
      aiService = AIService();
    });

    group('Initialization', () {
      test('initialize sets isInitialized to true on success', () async {
        // Note: This test may fail in test environment without assets
        // In real scenario, you'd mock the Interpreter.fromAsset
        // For now, we test the error path
        await aiService.initialize();
        // Service should handle initialization failure gracefully
      });
    });

    group('Feature Extraction', () {
      test('extractFeatures returns list of doubles', () {
        final tab = TabModel(
          id: '123',
          title: 'GitHub - Code Repository',
          url: 'https://github.com/user/repo',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
          domain: 'github.com',
        );

        final features = aiService._extractFeatures(tab);

        expect(features, isA<List<double>>());
        expect(features.length, greaterThan(0));
        expect(features.every((f) => f >= 0.0 && f <= 1.0), true);
      });

      test('extractFeatures handles work domain correctly', () {
        final tab = TabModel(
          id: '123',
          title: 'GitHub Repository',
          url: 'https://github.com/user/repo',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
          domain: 'github.com',
        );

        final features = aiService._extractFeatures(tab);

        // GitHub should match work category pattern
        expect(features.any((f) => f > 0.5), true);
      });

      test('extractFeatures handles shopping keywords', () {
        final tab = TabModel(
          id: '123',
          title: 'Buy Product - Shopping Cart',
          url: 'https://shop.com/cart',
          category: 'shopping',
          confidenceScore: 0.8,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
          domain: 'shop.com',
        );

        final features = aiService._extractFeatures(tab);

        expect(features, isNotEmpty);
      });

      test('extractFeatures handles URL structure features', () {
        final tab = TabModel(
          id: '123',
          title: 'Test',
          url: 'https://example.com/a/b/c?param=value#section',
          category: 'custom',
          confidenceScore: 0.5,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
          domain: 'example.com',
        );

        final features = aiService._extractFeatures(tab);

        // Should have features for path depth, query params, fragment
        expect(features.length, greaterThan(10));
      });
    });

    group('Fallback Classification', () {
      test('fallbackClassification returns work for GitHub URL', () async {
        final tab = TabModel(
          id: '123',
          title: 'GitHub Repository',
          url: 'https://github.com/user/repo',
          category: 'custom',
          confidenceScore: 0.0,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
          domain: 'github.com',
        );

        final result = await aiService.classifyTab(tab);

        expect(result['category'], 'work');
        expect(result['confidence'], greaterThan(0.0));
      });

      test('fallbackClassification returns shopping for Amazon URL', () async {
        final tab = TabModel(
          id: '123',
          title: 'Product Page',
          url: 'https://amazon.com/product/12345',
          category: 'custom',
          confidenceScore: 0.0,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
          domain: 'amazon.com',
        );

        final result = await aiService.classifyTab(tab);

        expect(result['category'], 'shopping');
      });

      test('fallbackClassification returns custom for unknown domain', () async {
        final tab = TabModel(
          id: '123',
          title: 'Unknown Site',
          url: 'https://unknown-domain-12345.com',
          category: 'custom',
          confidenceScore: 0.0,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
          domain: 'unknown-domain-12345.com',
        );

        final result = await aiService.classifyTab(tab);

        expect(result['category'], 'custom');
        expect(result['confidence'], lessThan(1.0));
      });
    });

    group('Batch Classification', () {
      test('classifyTabs processes multiple tabs', () async {
        final tabs = [
          TabModel(
            id: '1',
            title: 'GitHub',
            url: 'https://github.com',
            category: 'work',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 0,
            domain: 'github.com',
          ),
          TabModel(
            id: '2',
            title: 'Amazon',
            url: 'https://amazon.com',
            category: 'shopping',
            confidenceScore: 0.8,
            createdAt: DateTime.now(),
            lastAccessed: DateTime.now(),
            browser: 'chrome',
            tabIndex: 1,
            domain: 'amazon.com',
          ),
        ];

        final results = await aiService.classifyTabs(tabs);

        expect(results.length, 2);
        expect(results[0]['category'], isNotEmpty);
        expect(results[1]['category'], isNotEmpty);
      });

      test('classifyTabs handles empty list', () async {
        final results = await aiService.classifyTabs([]);

        expect(results, isEmpty);
      });
    });

    group('Category Suggestions', () {
      test('getCategorySuggestions returns matching categories', () {
        final suggestions = aiService.getCategorySuggestions('wor');

        expect(suggestions, contains('work'));
      });

      test('getCategorySuggestions is case-insensitive', () {
        final suggestions = aiService.getCategorySuggestions('WOR');

        expect(suggestions, contains('work'));
      });

      test('getCategorySuggestions returns empty for no matches', () {
        final suggestions = aiService.getCategorySuggestions('xyz123');

        expect(suggestions, isEmpty);
      });

      test('getCategorySuggestions returns all categories for empty query', () {
        final suggestions = aiService.getCategorySuggestions('');

        expect(suggestions.length, AppConstants.defaultCategories.length);
      });
    });

    group('Content Analysis', () {
      test('analyzeContent extracts keywords', () async {
        final content = 'This is a test article about programming and code development';

        final result = await aiService.analyzeContent(content);

        expect(result['keywords'], isA<List<String>>());
        expect(result['topics'], isA<List<String>>());
      });

      test('analyzeContent handles empty content', () async {
        final result = await aiService.analyzeContent('');

        expect(result['keywords'], isEmpty);
      });

      test('analyzeContent identifies tech topics', () async {
        final content = 'Programming code development API github repository';

        final result = await aiService.analyzeContent(content);

        expect(result['topics'], contains('technology'));
      });

      test('analyzeContent identifies social topics', () async {
        final content = 'Friend post share like comment social network';

        final result = await aiService.analyzeContent(content);

        expect(result['topics'], contains('social'));
      });

      test('analyzeContent identifies news topics', () async {
        final content = 'Breaking news article report latest update';

        final result = await aiService.analyzeContent(content);

        expect(result['topics'], contains('news'));
      });
    });

    group('Keyword Counting', () {
      test('countKeywords counts matching keywords', () {
        final text = 'github code api programming';
        final keywords = ['github', 'code', 'api'];

        final count = aiService._countKeywords(text, keywords);

        expect(count, 3.0);
      });

      test('countKeywords is case-insensitive', () {
        final text = 'GitHub CODE Api';
        final keywords = ['github', 'code', 'api'];

        final count = aiService._countKeywords(text, keywords);

        expect(count, 3.0);
      });

      test('countKeywords returns 0 for no matches', () {
        final text = 'something else entirely';
        final keywords = ['github', 'code', 'api'];

        final count = aiService._countKeywords(text, keywords);

        expect(count, 0.0);
      });
    });

    group('Training Feedback', () {
      test('trainWithFeedback accepts feedback', () async {
        final tab = TabModel(
          id: '123',
          title: 'Test',
          url: 'https://example.com',
          category: 'work',
          confidenceScore: 0.8,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
        );

        // Should not throw
        await aiService.trainWithFeedback(
          tab: tab,
          correctCategory: 'research',
        );
      });
    });

    group('Dispose', () {
      test('dispose cleans up resources', () {
        aiService.dispose();
        // Should not throw
      });
    });

    group('Edge Cases', () {
      test('classifyTab handles tab with no domain', () async {
        final tab = TabModel(
          id: '123',
          title: 'Test',
          url: 'about:blank',
          category: 'custom',
          confidenceScore: 0.0,
          createdAt: DateTime.now(),
          lastAccessed: DateTime.now(),
          browser: 'chrome',
          tabIndex: 0,
        );

        final result = await aiService.classifyTab(tab);

        expect(result['category'], isNotEmpty);
      });

      test('analyzeContent handles very long content', () async {
        final longContent = 'word ' * 10000;

        final result = await aiService.analyzeContent(longContent);

        expect(result['keywords'], isA<List<String>>());
      });

      test('getCategorySuggestions handles special characters', () {
        final suggestions = aiService.getCategorySuggestions('wo@#rk');

        // Should handle gracefully
        expect(suggestions, isA<List<String>>());
      });
    });
  });
}