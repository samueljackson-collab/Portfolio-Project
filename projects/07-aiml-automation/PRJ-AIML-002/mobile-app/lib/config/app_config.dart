/// Application-wide configuration constants
class AppConfig {
  // ML Model Configuration
  static const int maxTokens = 512;
  static const double classificationThreshold = 0.7;
  static const int clusteringMinSamples = 2;
  static const double clusteringEpsilon = 0.4;

  // Sync Configuration
  static const Duration syncInterval = Duration(minutes: 5);
  static const bool enableOfflineMode = true;
  static const int maxSyncRetries = 3;
  static const Duration syncRetryDelay = Duration(seconds: 2);

  // UI Configuration
  static const int maxTabsPerGroup = 50;
  static const bool enableAnimations = true;
  static const Duration animationDuration = Duration(milliseconds: 300);

  // Storage Configuration
  static const int maxLocalTabs = 10000;
  static const Duration cacheExpiration = Duration(days: 30);
  static const int maxCacheSize = 500 * 1024 * 1024; // 500 MB

  // Native Messaging
  static const String nativeHostName = 'com.taborganizer.native_host';
  static const int nativeHostPort = 8765;
  static const String nativeHostUrl = 'ws://localhost:$nativeHostPort';

  // Security
  static const int rsaKeySize = 4096;
  static const int aesKeySize = 256;
  static const int pbkdf2Iterations = 100000;

  // Performance
  static const int maxBatchSize = 10;
  static const bool enableGpuAcceleration = true;
  static const Duration inferenceTimeout = Duration(seconds: 5);

  // Categories
  static const List<String> categories = [
    'Work',
    'Research',
    'Shopping',
    'Social Media',
    'Entertainment',
    'News',
    'Finance',
    'Education',
    'Other',
  ];

  // Category Colors
  static const Map<String, int> categoryColors = {
    'Work': 0xFF2196F3,
    'Research': 0xFF9C27B0,
    'Shopping': 0xFFFF9800,
    'Social Media': 0xFFE91E63,
    'Entertainment': 0xFFF44336,
    'News': 0xFF4CAF50,
    'Finance': 0xFF00BCD4,
    'Education': 0xFF3F51B5,
    'Other': 0xFF9E9E9E,
  };
}
