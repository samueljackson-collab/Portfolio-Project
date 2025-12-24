import 'package:flutter/material.dart';

class AppConstants {
  static const String appName = 'Tab Organizer';
  static const String appVersion = '1.0.0';

  // Colors
  static const Color primaryColor = Color(0xFF6366F1); // Indigo
  static const Color secondaryColor = Color(0xFF8B5CF6); // Purple
  static const Color accentColor = Color(0xFF10B981); // Green

  // Category Colors
  static const Map<String, Color> categoryColors = {
    'work': Color(0xFF3B82F6), // Blue
    'research': Color(0xFF8B5CF6), // Purple
    'shopping': Color(0xFFEC4899), // Pink
    'social': Color(0xFF10B981), // Green
    'entertainment': Color(0xFFF59E0B), // Amber
    'news': Color(0xFFEF4444), // Red
    'custom': Color(0xFF6B7280), // Gray
  };

  // AI Classification Thresholds
  static const double minConfidenceScore = 0.6;
  static const int maxTabsPerGroup = 50;
  static const int maxRecentTabs = 100;

  // Sync Settings
  static const Duration syncInterval = Duration(minutes: 5);
  static const int maxRetryAttempts = 3;

  // Native Messaging
  static const String nativeHostName = 'com.taborganizer.native';
  static const int nativeMessageTimeout = 5000; // ms

  // Storage Keys
  static const String hiveBoxName = 'tab_organizer';
  static const String settingsBoxName = 'settings';
  static const String tabGroupsBoxName = 'tab_groups';

  // Default Categories
  static const List<String> defaultCategories = [
    'work',
    'research',
    'shopping',
    'social',
    'entertainment',
    'news',
  ];

  // URL Patterns for Classification
  static const Map<String, List<String>> categoryPatterns = {
    'work': [
      'github.com',
      'gitlab.com',
      'stackoverflow.com',
      'docs.google.com',
      'notion.so',
      'slack.com',
      'teams.microsoft.com',
      'zoom.us',
    ],
    'research': [
      'wikipedia.org',
      'scholar.google.com',
      'arxiv.org',
      'medium.com',
      'dev.to',
    ],
    'shopping': [
      'amazon.com',
      'ebay.com',
      'etsy.com',
      'shopify.com',
      'walmart.com',
    ],
    'social': [
      'facebook.com',
      'twitter.com',
      'instagram.com',
      'linkedin.com',
      'reddit.com',
    ],
    'entertainment': [
      'youtube.com',
      'netflix.com',
      'spotify.com',
      'twitch.tv',
      'hulu.com',
    ],
    'news': [
      'news.google.com',
      'bbc.com',
      'cnn.com',
      'reuters.com',
      'nytimes.com',
    ],
  };
}
