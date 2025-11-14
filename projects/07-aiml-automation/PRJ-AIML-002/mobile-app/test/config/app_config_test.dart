import 'package:flutter_test/flutter_test.dart';
import 'package:tab_organizer/config/app_config.dart';

void main() {
  group('AppConfig - ML Configuration', () {
    test('maxTokens is positive', () {
      expect(AppConfig.maxTokens, greaterThan(0));
      expect(AppConfig.maxTokens, 512);
    });

    test('classificationThreshold is valid probability', () {
      expect(AppConfig.classificationThreshold, greaterThanOrEqualTo(0.0));
      expect(AppConfig.classificationThreshold, lessThanOrEqualTo(1.0));
      expect(AppConfig.classificationThreshold, 0.7);
    });

    test('clusteringMinSamples is positive', () {
      expect(AppConfig.clusteringMinSamples, greaterThan(0));
      expect(AppConfig.clusteringMinSamples, 2);
    });

    test('clusteringEpsilon is valid', () {
      expect(AppConfig.clusteringEpsilon, greaterThan(0.0));
      expect(AppConfig.clusteringEpsilon, lessThanOrEqualTo(1.0));
      expect(AppConfig.clusteringEpsilon, 0.4);
    });
  });

  group('AppConfig - Sync Configuration', () {
    test('syncInterval is positive', () {
      expect(AppConfig.syncInterval.inMilliseconds, greaterThan(0));
      expect(AppConfig.syncInterval, Duration(minutes: 5));
    });

    test('enableOfflineMode is boolean', () {
      expect(AppConfig.enableOfflineMode, isA<bool>());
      expect(AppConfig.enableOfflineMode, true);
    });

    test('maxSyncRetries is positive', () {
      expect(AppConfig.maxSyncRetries, greaterThan(0));
      expect(AppConfig.maxSyncRetries, 3);
    });

    test('syncRetryDelay is positive', () {
      expect(AppConfig.syncRetryDelay.inMilliseconds, greaterThan(0));
      expect(AppConfig.syncRetryDelay, Duration(seconds: 2));
    });
  });

  group('AppConfig - UI Configuration', () {
    test('maxTabsPerGroup is positive', () {
      expect(AppConfig.maxTabsPerGroup, greaterThan(0));
      expect(AppConfig.maxTabsPerGroup, 50);
    });

    test('enableAnimations is boolean', () {
      expect(AppConfig.enableAnimations, isA<bool>());
      expect(AppConfig.enableAnimations, true);
    });

    test('animationDuration is positive', () {
      expect(AppConfig.animationDuration.inMilliseconds, greaterThan(0));
      expect(AppConfig.animationDuration, Duration(milliseconds: 300));
    });
  });

  group('AppConfig - Storage Configuration', () {
    test('maxLocalTabs is positive', () {
      expect(AppConfig.maxLocalTabs, greaterThan(0));
      expect(AppConfig.maxLocalTabs, 10000);
    });

    test('cacheExpiration is positive', () {
      expect(AppConfig.cacheExpiration.inDays, greaterThan(0));
      expect(AppConfig.cacheExpiration, Duration(days: 30));
    });

    test('maxCacheSize is positive', () {
      expect(AppConfig.maxCacheSize, greaterThan(0));
      expect(AppConfig.maxCacheSize, 500 * 1024 * 1024);
    });
  });

  group('AppConfig - Native Messaging', () {
    test('nativeHostName is valid', () {
      expect(AppConfig.nativeHostName, isNotEmpty);
      expect(AppConfig.nativeHostName, 'com.taborganizer.native_host');
    });

    test('nativeHostPort is valid', () {
      expect(AppConfig.nativeHostPort, greaterThan(0));
      expect(AppConfig.nativeHostPort, lessThan(65536));
      expect(AppConfig.nativeHostPort, 8765);
    });

    test('nativeHostUrl is valid URL', () {
      expect(AppConfig.nativeHostUrl, startsWith('ws://'));
      expect(AppConfig.nativeHostUrl, contains('localhost'));
      expect(AppConfig.nativeHostUrl, contains('8765'));
    });
  });

  group('AppConfig - Security', () {
    test('rsaKeySize is valid', () {
      expect(AppConfig.rsaKeySize, greaterThan(0));
      expect(AppConfig.rsaKeySize, 4096);
    });

    test('aesKeySize is valid', () {
      expect(AppConfig.aesKeySize, greaterThan(0));
      expect(AppConfig.aesKeySize, 256);
    });

    test('pbkdf2Iterations is sufficient', () {
      expect(AppConfig.pbkdf2Iterations, greaterThanOrEqualTo(10000));
      expect(AppConfig.pbkdf2Iterations, 100000);
    });
  });

  group('AppConfig - Performance', () {
    test('maxBatchSize is positive', () {
      expect(AppConfig.maxBatchSize, greaterThan(0));
      expect(AppConfig.maxBatchSize, 10);
    });

    test('enableGpuAcceleration is boolean', () {
      expect(AppConfig.enableGpuAcceleration, isA<bool>());
      expect(AppConfig.enableGpuAcceleration, true);
    });

    test('inferenceTimeout is positive', () {
      expect(AppConfig.inferenceTimeout.inMilliseconds, greaterThan(0));
      expect(AppConfig.inferenceTimeout, Duration(seconds: 5));
    });
  });

  group('AppConfig - Categories', () {
    test('categories list has all expected entries', () {
      expect(AppConfig.categories.length, 9);
      expect(AppConfig.categories, contains('Work'));
      expect(AppConfig.categories, contains('Research'));
      expect(AppConfig.categories, contains('Shopping'));
      expect(AppConfig.categories, contains('Social Media'));
      expect(AppConfig.categories, contains('Entertainment'));
      expect(AppConfig.categories, contains('News'));
      expect(AppConfig.categories, contains('Finance'));
      expect(AppConfig.categories, contains('Education'));
      expect(AppConfig.categories, contains('Other'));
    });

    test('categories are unique', () {
      final uniqueCategories = AppConfig.categories.toSet();
      expect(uniqueCategories.length, AppConfig.categories.length);
    });
  });

  group('AppConfig - Category Colors', () {
    test('categoryColors has entry for each category', () {
      expect(AppConfig.categoryColors.length, 9);
      for (final category in AppConfig.categories) {
        expect(AppConfig.categoryColors.containsKey(category), true);
      }
    });

    test('all colors are valid ARGB values', () {
      for (final color in AppConfig.categoryColors.values) {
        expect(color, greaterThanOrEqualTo(0));
        // Alpha channel should be FF (fully opaque)
        expect((color >> 24) & 0xFF, 0xFF);
      }
    });

    test('colors are unique', () {
      final colors = AppConfig.categoryColors.values.toSet();
      expect(colors.length, AppConfig.categoryColors.length);
    });

    test('specific color values match expectations', () {
      expect(AppConfig.categoryColors['Work'], 0xFF2196F3);
      expect(AppConfig.categoryColors['Research'], 0xFF9C27B0);
      expect(AppConfig.categoryColors['Shopping'], 0xFFFF9800);
      expect(AppConfig.categoryColors['Social Media'], 0xFFE91E63);
      expect(AppConfig.categoryColors['Entertainment'], 0xFFF44336);
      expect(AppConfig.categoryColors['News'], 0xFF4CAF50);
      expect(AppConfig.categoryColors['Finance'], 0xFF00BCD4);
      expect(AppConfig.categoryColors['Education'], 0xFF3F51B5);
      expect(AppConfig.categoryColors['Other'], 0xFF9E9E9E);
    });
  });

  group('AppConfig - Value Ranges', () {
    test('classification threshold is reasonable', () {
      // Should be high enough to avoid false positives
      expect(AppConfig.classificationThreshold, greaterThanOrEqualTo(0.5));
    });

    test('clustering epsilon allows meaningful grouping', () {
      // Should allow some flexibility but not too much
      expect(AppConfig.clusteringEpsilon, greaterThan(0.1));
      expect(AppConfig.clusteringEpsilon, lessThan(0.9));
    });

    test('sync interval is reasonable', () {
      // Not too frequent to avoid excessive API calls
      expect(AppConfig.syncInterval.inMinutes, greaterThanOrEqualTo(1));
      // Not too infrequent to maintain freshness
      expect(AppConfig.syncInterval.inMinutes, lessThanOrEqualTo(60));
    });

    test('cache expiration is reasonable', () {
      // At least a week
      expect(AppConfig.cacheExpiration.inDays, greaterThanOrEqualTo(7));
      // Not more than a year
      expect(AppConfig.cacheExpiration.inDays, lessThanOrEqualTo(365));
    });
  });

  group('AppConfig - Security Best Practices', () {
    test('RSA key size meets security standards', () {
      // Minimum 2048 bits for security
      expect(AppConfig.rsaKeySize, greaterThanOrEqualTo(2048));
    });

    test('AES key size meets security standards', () {
      // Should be 128, 192, or 256 bits
      expect([128, 192, 256], contains(AppConfig.aesKeySize));
    });

    test('PBKDF2 iterations meet OWASP recommendations', () {
      // OWASP recommends at least 10,000 iterations
      expect(AppConfig.pbkdf2Iterations, greaterThanOrEqualTo(10000));
    });
  });

  group('AppConfig - Performance Constraints', () {
    test('maxBatchSize is reasonable for memory usage', () {
      // Should be small enough to fit in memory
      expect(AppConfig.maxBatchSize, lessThanOrEqualTo(100));
    });

    test('inferenceTimeout prevents hanging', () {
      // Should be long enough for inference but not too long
      expect(AppConfig.inferenceTimeout.inSeconds, greaterThanOrEqualTo(1));
      expect(AppConfig.inferenceTimeout.inSeconds, lessThanOrEqualTo(30));
    });

    test('animation duration feels responsive', () {
      // Animations should be quick but not jarring
      expect(AppConfig.animationDuration.inMilliseconds, greaterThanOrEqualTo(100));
      expect(AppConfig.animationDuration.inMilliseconds, lessThanOrEqualTo(1000));
    });
  });
}