import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
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
    // TODO: Implement actual sync logic with local database
    // This is a placeholder implementation
    return 0;
  }

  /// Download tab groups from cloud
  Future<int> _downloadTabGroups(String userId) async {
    try {
      final snapshot = await _firestore
          .collection('users')
          .doc(userId)
          .collection('tabGroups')
          .where('updatedAt', isGreaterThan: _getLastSyncTime())
          .get();

      int count = 0;
      for (final doc in snapshot.docs) {
        final data = doc.data();

        // Decrypt data
        final decryptedData = await _encryption.decrypt(
          data['encryptedData'] as String,
        );

        // TODO: Save to local database
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
    // TODO: Implement actual sync logic
    return 0;
  }

  /// Download tabs from cloud
  Future<int> _downloadTabs(String userId) async {
    // TODO: Implement actual sync logic
    return 0;
  }

  /// Get last sync timestamp
  DateTime _getLastSyncTime() {
    // TODO: Retrieve from local storage
    return DateTime.now().subtract(AppConfig.syncInterval);
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
