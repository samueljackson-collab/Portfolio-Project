import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Provider for managing app settings
class SettingsProvider with ChangeNotifier {
  late SharedPreferences _prefs;
  bool _isInitialized = false;

  // Settings
  ThemeMode _themeMode = ThemeMode.system;
  bool _cloudSyncEnabled = false;
  bool _autoGroupEnabled = true;
  bool _showDuplicateWarnings = true;
  bool _enableNotifications = true;
  int _syncIntervalMinutes = 5;
  double _minConfidenceScore = 0.6;

  // Getters
  ThemeMode get themeMode => _themeMode;
  bool get cloudSyncEnabled => _cloudSyncEnabled;
  bool get autoGroupEnabled => _autoGroupEnabled;
  bool get showDuplicateWarnings => _showDuplicateWarnings;
  bool get enableNotifications => _enableNotifications;
  int get syncIntervalMinutes => _syncIntervalMinutes;
  double get minConfidenceScore => _minConfidenceScore;
  bool get isInitialized => _isInitialized;

  /// Initialize settings
  Future<void> initialize() async {
    try {
      _prefs = await SharedPreferences.getInstance();
      await _loadSettings();
      _isInitialized = true;
      notifyListeners();
    } catch (e) {
      debugPrint('Error initializing settings: $e');
    }
  }

  /// Load settings from storage
  Future<void> _loadSettings() async {
    final themeModeIndex = _prefs.getInt('themeMode') ?? ThemeMode.system.index;
    _themeMode = ThemeMode.values[themeModeIndex];

    _cloudSyncEnabled = _prefs.getBool('cloudSyncEnabled') ?? false;
    _autoGroupEnabled = _prefs.getBool('autoGroupEnabled') ?? true;
    _showDuplicateWarnings = _prefs.getBool('showDuplicateWarnings') ?? true;
    _enableNotifications = _prefs.getBool('enableNotifications') ?? true;
    _syncIntervalMinutes = _prefs.getInt('syncIntervalMinutes') ?? 5;
    _minConfidenceScore = _prefs.getDouble('minConfidenceScore') ?? 0.6;
  }

  /// Set theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    _themeMode = mode;
    await _prefs.setInt('themeMode', mode.index);
    notifyListeners();
  }

  /// Toggle dark mode
  Future<void> toggleDarkMode() async {
    final newMode = _themeMode == ThemeMode.dark
        ? ThemeMode.light
        : ThemeMode.dark;
    await setThemeMode(newMode);
  }

  /// Enable/disable cloud sync
  Future<void> setCloudSyncEnabled(bool enabled) async {
    _cloudSyncEnabled = enabled;
    await _prefs.setBool('cloudSyncEnabled', enabled);
    notifyListeners();
  }

  /// Enable/disable auto grouping
  Future<void> setAutoGroupEnabled(bool enabled) async {
    _autoGroupEnabled = enabled;
    await _prefs.setBool('autoGroupEnabled', enabled);
    notifyListeners();
  }

  /// Enable/disable duplicate warnings
  Future<void> setShowDuplicateWarnings(bool enabled) async {
    _showDuplicateWarnings = enabled;
    await _prefs.setBool('showDuplicateWarnings', enabled);
    notifyListeners();
  }

  /// Enable/disable notifications
  Future<void> setEnableNotifications(bool enabled) async {
    _enableNotifications = enabled;
    await _prefs.setBool('enableNotifications', enabled);
    notifyListeners();
  }

  /// Set sync interval
  Future<void> setSyncIntervalMinutes(int minutes) async {
    _syncIntervalMinutes = minutes;
    await _prefs.setInt('syncIntervalMinutes', minutes);
    notifyListeners();
  }

  /// Set minimum confidence score
  Future<void> setMinConfidenceScore(double score) async {
    _minConfidenceScore = score;
    await _prefs.setDouble('minConfidenceScore', score);
    notifyListeners();
  }

  /// Reset all settings to default
  Future<void> resetToDefaults() async {
    await setThemeMode(ThemeMode.system);
    await setCloudSyncEnabled(false);
    await setAutoGroupEnabled(true);
    await setShowDuplicateWarnings(true);
    await setEnableNotifications(true);
    await setSyncIntervalMinutes(5);
    await setMinConfidenceScore(0.6);
  }

  /// Get all settings as map
  Map<String, dynamic> getAllSettings() {
    return {
      'themeMode': _themeMode.index,
      'cloudSyncEnabled': _cloudSyncEnabled,
      'autoGroupEnabled': _autoGroupEnabled,
      'showDuplicateWarnings': _showDuplicateWarnings,
      'enableNotifications': _enableNotifications,
      'syncIntervalMinutes': _syncIntervalMinutes,
      'minConfidenceScore': _minConfidenceScore,
    };
  }

  /// Import settings from map
  Future<void> importSettings(Map<String, dynamic> settings) async {
    if (settings.containsKey('themeMode')) {
      await setThemeMode(ThemeMode.values[settings['themeMode']]);
    }
    if (settings.containsKey('cloudSyncEnabled')) {
      await setCloudSyncEnabled(settings['cloudSyncEnabled']);
    }
    if (settings.containsKey('autoGroupEnabled')) {
      await setAutoGroupEnabled(settings['autoGroupEnabled']);
    }
    if (settings.containsKey('showDuplicateWarnings')) {
      await setShowDuplicateWarnings(settings['showDuplicateWarnings']);
    }
    if (settings.containsKey('enableNotifications')) {
      await setEnableNotifications(settings['enableNotifications']);
    }
    if (settings.containsKey('syncIntervalMinutes')) {
      await setSyncIntervalMinutes(settings['syncIntervalMinutes']);
    }
    if (settings.containsKey('minConfidenceScore')) {
      await setMinConfidenceScore(settings['minConfidenceScore']);
    }
  }
}
