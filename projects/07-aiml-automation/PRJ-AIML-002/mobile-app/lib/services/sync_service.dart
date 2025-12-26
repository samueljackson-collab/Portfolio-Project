import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:hive/hive.dart';
import 'package:logger/logger.dart';

import '../config/app_config.dart';
import '../models/tab.dart';
import '../models/tab_group.dart';
import 'encryption_service.dart';

/// Cloud synchronization service using Firebase
class SyncService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final EncryptionService _encryption = EncryptionService();
  final Logger _logger = Logger();

  static const String _tabBoxName = 'tabs';
  static const String _tabGroupBoxName = 'tab_groups';
  static const String _syncMetadataBoxName = 'sync_metadata';
  static const String _lastSyncKey = 'last_sync';

  Timer? _syncTimer;
  bool _isSyncing = false;

  /// Start automatic sync
  void startAutoSync() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(AppConfig.syncInterval, (_) => sync());
    _logger.i('Auto-sync started (interval: ${AppConfig.syncInterval})');
  }

  /// Stop automatic sync
  void stopAutoSync() {
    _syncTimer?.cancel();
    _syncTimer = null;
    _logger.i('Auto-sync stopped');
  }

  /// Synchronize data with cloud
  Future<SyncResult> sync() async {
    if (_isSyncing) {
      _logger.w('Sync already in progress, skipping');
      return SyncResult.skipped();
    }

    _isSyncing = true;
    final startTime = DateTime.now();

    try {
      _logger.i('Starting sync...');

      final user = _auth.currentUser;
      if (user == null) {
        _logger.w('User not authenticated, skipping sync');
        return SyncResult.failed('Not authenticated');
      }

      // Sync tab groups
      final groupsUploaded = await _syncTabGroups(user.uid);
      final groupsDownloaded = await _downloadTabGroups(user.uid);

      // Sync tabs
      final tabsUploaded = await _syncTabs(user.uid);
      final tabsDownloaded = await _downloadTabs(user.uid);

      await _updateLastSyncTime(DateTime.now());

      final duration = DateTime.now().difference(startTime);
      _logger.i('Sync completed in ${duration.inMilliseconds}ms');

      return SyncResult.success(
        groupsUploaded: groupsUploaded,
        groupsDownloaded: groupsDownloaded,
        tabsUploaded: tabsUploaded,
        tabsDownloaded: tabsDownloaded,
        duration: duration,
      );
    } catch (e) {
      _logger.e('Sync failed: $e');
      return SyncResult.failed(e.toString());
    } finally {
      _isSyncing = false;
    }
  }

  /// Upload modified tab groups to cloud
  Future<int> _syncTabGroups(String userId) async {
    try {
      final box = await Hive.openBox<Map>(_tabGroupBoxName);
      final lastSync = await _getLastSyncTime();
      int uploaded = 0;

      for (final key in box.keys) {
        final data = Map<String, dynamic>.from(box.get(key)!);
        final updatedAt = _parseTimestamp(data['updatedAt']);
        if (updatedAt.isBefore(lastSync)) {
          continue;
        }

        final groupId = (data['id'] ?? key).toString();
        data['id'] = groupId;
        data['updatedAt'] = updatedAt.toIso8601String();

        final encryptedData = await _encryption.encrypt(data);

        await _firestore
            .collection('users')
            .doc(userId)
            .collection('tabGroups')
            .doc(groupId)
            .set({
          'name': data['name'] ?? 'Untitled',
          'category': data['category'] ?? 'other',
          'createdAt': _parseTimestamp(data['createdAt']),
          'updatedAt': DateTime.now(),
          'encryptedData': encryptedData,
        }, SetOptions(merge: true));

        uploaded++;
      }

      return uploaded;
    } catch (e) {
      _logger.e('Failed to upload tab groups: $e');
      return 0;
    }
  }

  /// Download tab groups from cloud
  Future<int> _downloadTabGroups(String userId) async {
    try {
      final box = await Hive.openBox<Map>(_tabGroupBoxName);
      final lastSync = await _getLastSyncTime();
      final snapshot = await _firestore
          .collection('users')
          .doc(userId)
          .collection('tabGroups')
          .where('updatedAt', isGreaterThan: lastSync)
          .get();

      int count = 0;
      for (final doc in snapshot.docs) {
        final data = doc.data();

        // Decrypt data
        final decryptedData = await _encryption.decrypt(
          data['encryptedData'] as String,
        );

        final updatedAt = _parseTimestamp(data['updatedAt']);
        final groupId = (decryptedData['id'] ?? doc.id).toString();
        decryptedData['id'] = groupId;
        decryptedData['updatedAt'] = updatedAt.toIso8601String();

        await box.put(groupId, Map<String, dynamic>.from(decryptedData));
        count++;
      }

      return count;
    } catch (e) {
      _logger.e('Failed to download tab groups: $e');
      return 0;
    }
  }

  /// Upload modified tabs to cloud
  Future<int> _syncTabs(String userId) async {
    try {
      final box = await Hive.openBox<Map>(_tabBoxName);
      final lastSync = await _getLastSyncTime();
      int uploaded = 0;

      for (final entry in box.toMap().entries) {
        final data = Map<String, dynamic>.from(entry.value);
        final updatedAt = _parseTimestamp(data['updatedAt']);
        if (updatedAt.isBefore(lastSync)) {
          continue;
        }

        final tabId = (data['id'] ?? entry.key).toString();
        data['id'] = tabId;
        data['updatedAt'] = updatedAt.toIso8601String();

        final encryptedData = await _encryption.encrypt(data);

        await _firestore
            .collection('users')
            .doc(userId)
            .collection('tabs')
            .doc(tabId)
            .set({
          'title': data['title'] ?? 'Untitled',
          'url': data['url'] ?? '',
          'category': data['category'] ?? 'other',
          'createdAt': _parseTimestamp(data['createdAt']),
          'updatedAt': DateTime.now(),
          'encryptedData': encryptedData,
        }, SetOptions(merge: true));

        uploaded++;
      }

      return uploaded;
    } catch (e) {
      _logger.e('Failed to upload tabs: $e');
      return 0;
    }
  }

  /// Download tabs from cloud
  Future<int> _downloadTabs(String userId) async {
    try {
      final box = await Hive.openBox<Map>(_tabBoxName);
      final lastSync = await _getLastSyncTime();

      final snapshot = await _firestore
          .collection('users')
          .doc(userId)
          .collection('tabs')
          .where('updatedAt', isGreaterThan: lastSync)
          .get();

      int count = 0;
      for (final doc in snapshot.docs) {
        final data = doc.data();
        final decryptedData = await _encryption.decrypt(
          data['encryptedData'] as String,
        );
        final updatedAt = _parseTimestamp(data['updatedAt']);
        final tabId = (decryptedData['id'] ?? doc.id).toString();
        decryptedData['id'] = tabId;
        decryptedData['updatedAt'] = updatedAt.toIso8601String();

        await box.put(tabId, Map<String, dynamic>.from(decryptedData));
        count++;
      }

      return count;
    } catch (e) {
      _logger.e('Failed to download tabs: $e');
      return 0;
    }
  }

  /// Get last sync timestamp
  Future<DateTime> _getLastSyncTime() async {
    try {
      final box = Hive.isBoxOpen(_syncMetadataBoxName)
          ? Hive.box<Map>(_syncMetadataBoxName)
          : await Hive.openBox<Map>(_syncMetadataBoxName);
      final stored = box.get(_lastSyncKey);
      if (stored == null) {
        return DateTime.now().subtract(AppConfig.syncInterval);
      }
      return _parseTimestamp(stored['value']);
    } catch (_) {
      return DateTime.now().subtract(AppConfig.syncInterval);
    }
  }

  Future<void> _updateLastSyncTime(DateTime timestamp) async {
    final box = await Hive.openBox<Map>(_syncMetadataBoxName);
    await box.put(_lastSyncKey, {'value': timestamp.toIso8601String()});
  }

  DateTime _parseTimestamp(dynamic value) {
    if (value == null) {
      return DateTime.fromMillisecondsSinceEpoch(0);
    }
    if (value is DateTime) {
      return value;
    }
    if (value is Timestamp) {
      return value.toDate();
    }
    if (value is int) {
      return DateTime.fromMillisecondsSinceEpoch(value);
    }
    if (value is String) {
      return DateTime.tryParse(value) ??
          DateTime.fromMillisecondsSinceEpoch(0);
    }
    return DateTime.fromMillisecondsSinceEpoch(0);
  }

  /// Upload a single tab group
  Future<void> uploadTabGroup(TabGroup group) async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      // Encrypt data
      final encryptedData = await _encryption.encrypt(group.toJson());

      await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('tabGroups')
          .doc(group.id)
          .set({
        'name': group.name,
        'category': group.category.name,
        'createdAt': group.createdAt,
        'updatedAt': DateTime.now(),
        'encryptedData': encryptedData,
      });

      _logger.d('Uploaded tab group: ${group.name}');
    } catch (e) {
      _logger.e('Failed to upload tab group: $e');
    }
  }

  /// Delete a tab group from cloud
  Future<void> deleteTabGroup(String groupId) async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('tabGroups')
          .doc(groupId)
          .delete();

      _logger.d('Deleted tab group from cloud: $groupId');
    } catch (e) {
      _logger.e('Failed to delete tab group: $e');
    }
  }

  void dispose() {
    stopAutoSync();
  }
}

/// Sync operation result
class SyncResult {
  final bool success;
  final int groupsUploaded;
  final int groupsDownloaded;
  final int tabsUploaded;
  final int tabsDownloaded;
  final Duration? duration;
  final String? error;

  SyncResult({
    required this.success,
    this.groupsUploaded = 0,
    this.groupsDownloaded = 0,
    this.tabsUploaded = 0,
    this.tabsDownloaded = 0,
    this.duration,
    this.error,
  });

  factory SyncResult.success({
    required int groupsUploaded,
    required int groupsDownloaded,
    required int tabsUploaded,
    required int tabsDownloaded,
    required Duration duration,
  }) {
    return SyncResult(
      success: true,
      groupsUploaded: groupsUploaded,
      groupsDownloaded: groupsDownloaded,
      tabsUploaded: tabsUploaded,
      tabsDownloaded: tabsDownloaded,
      duration: duration,
    );
  }

  factory SyncResult.failed(String error) {
    return SyncResult(
      success: false,
      error: error,
    );
  }

  factory SyncResult.skipped() {
    return SyncResult(
      success: false,
      error: 'Sync already in progress',
    );
  }

  @override
  String toString() {
    if (!success) return 'SyncResult(failed: $error)';

    return 'SyncResult(uploaded: $groupsUploaded groups, $tabsUploaded tabs; '
           'downloaded: $groupsDownloaded groups, $tabsDownloaded tabs; '
           'duration: ${duration?.inMilliseconds}ms)';
  }
}
