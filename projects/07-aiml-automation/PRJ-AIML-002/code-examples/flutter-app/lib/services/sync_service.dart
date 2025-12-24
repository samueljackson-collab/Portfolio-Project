import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/tab_model.dart';
import '../utils/constants.dart';

/// Service for cloud synchronization using Firebase
class SyncService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  bool _isSyncing = false;
  Timer? _syncTimer;

  /// Initialize sync service
  Future<void> initialize() async {
    try {
      // Check if user is authenticated
      if (_auth.currentUser == null) {
        print('User not authenticated, sync disabled');
        return;
      }

      // Start periodic sync
      startPeriodicSync();

      print('Sync Service initialized successfully');
    } catch (e) {
      print('Error initializing Sync Service: $e');
    }
  }

  /// Start periodic synchronization
  void startPeriodicSync() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(AppConstants.syncInterval, (_) {
      syncAll();
    });
  }

  /// Stop periodic synchronization
  void stopPeriodicSync() {
    _syncTimer?.cancel();
    _syncTimer = null;
  }

  /// Sync all data
  Future<void> syncAll() async {
    if (_isSyncing) {
      print('Sync already in progress');
      return;
    }

    _isSyncing = true;

    try {
      await Future.wait([
        syncTabs(),
        syncGroups(),
      ]);

      print('Sync completed successfully');
    } catch (e) {
      print('Error during sync: $e');
    } finally {
      _isSyncing = false;
    }
  }

  /// Sync tabs to cloud
  Future<void> syncTabs() async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      // Get local tabs (would come from TabService in real implementation)
      final localTabs = <TabModel>[]; // Placeholder

      // Upload each tab
      for (final tab in localTabs) {
        await _firestore
            .collection('users')
            .doc(user.uid)
            .collection('tabs')
            .doc(tab.id)
            .set(
              tab.toJson(),
              SetOptions(merge: true),
            );
      }

      print('Synced ${localTabs.length} tabs');
    } catch (e) {
      print('Error syncing tabs: $e');
      rethrow;
    }
  }

  /// Sync groups to cloud
  Future<void> syncGroups() async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      // Get local groups (would come from TabService in real implementation)
      final localGroups = <TabGroup>[]; // Placeholder

      // Upload each group
      for (final group in localGroups) {
        await _firestore
            .collection('users')
            .doc(user.uid)
            .collection('groups')
            .doc(group.id)
            .set(
              group.toJson(),
              SetOptions(merge: true),
            );
      }

      print('Synced ${localGroups.length} groups');
    } catch (e) {
      print('Error syncing groups: $e');
      rethrow;
    }
  }

  /// Download tabs from cloud
  Future<List<TabModel>> downloadTabs() async {
    final user = _auth.currentUser;
    if (user == null) return [];

    try {
      final snapshot = await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('tabs')
          .get();

      final tabs = snapshot.docs
          .map((doc) => TabModel.fromJson(doc.data()))
          .toList();

      print('Downloaded ${tabs.length} tabs');
      return tabs;
    } catch (e) {
      print('Error downloading tabs: $e');
      return [];
    }
  }

  /// Download groups from cloud
  Future<List<TabGroup>> downloadGroups() async {
    final user = _auth.currentUser;
    if (user == null) return [];

    try {
      final snapshot = await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('groups')
          .get();

      final groups = snapshot.docs
          .map((doc) => TabGroup.fromJson(doc.data()))
          .toList();

      print('Downloaded ${groups.length} groups');
      return groups;
    } catch (e) {
      print('Error downloading groups: $e');
      return [];
    }
  }

  /// Listen to real-time tab updates
  Stream<List<TabModel>> watchTabs() {
    final user = _auth.currentUser;
    if (user == null) return Stream.value([]);

    return _firestore
        .collection('users')
        .doc(user.uid)
        .collection('tabs')
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => TabModel.fromJson(doc.data()))
          .toList();
    });
  }

  /// Listen to real-time group updates
  Stream<List<TabGroup>> watchGroups() {
    final user = _auth.currentUser;
    if (user == null) return Stream.value([]);

    return _firestore
        .collection('users')
        .doc(user.uid)
        .collection('groups')
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => TabGroup.fromJson(doc.data()))
          .toList();
    });
  }

  /// Delete tab from cloud
  Future<void> deleteTab(String tabId) async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('tabs')
          .doc(tabId)
          .delete();

      print('Deleted tab from cloud: $tabId');
    } catch (e) {
      print('Error deleting tab: $e');
      rethrow;
    }
  }

  /// Delete group from cloud
  Future<void> deleteGroup(String groupId) async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('groups')
          .doc(groupId)
          .delete();

      print('Deleted group from cloud: $groupId');
    } catch (e) {
      print('Error deleting group: $e');
      rethrow;
    }
  }

  /// Check if cloud sync is available
  Future<bool> isCloudSyncAvailable() async {
    try {
      final user = _auth.currentUser;
      if (user == null) return false;

      // Test Firestore connection
      await _firestore
          .collection('users')
          .doc(user.uid)
          .get()
          .timeout(const Duration(seconds: 5));

      return true;
    } catch (e) {
      print('Cloud sync not available: $e');
      return false;
    }
  }

  /// Get sync status
  Map<String, dynamic> getSyncStatus() {
    return {
      'isSyncing': _isSyncing,
      'isAuthenticated': _auth.currentUser != null,
      'userId': _auth.currentUser?.uid,
      'email': _auth.currentUser?.email,
      'periodicSyncEnabled': _syncTimer != null && _syncTimer!.isActive,
    };
  }

  /// Enable cloud sync
  Future<void> enableCloudSync() async {
    // Sign in anonymously if not authenticated
    if (_auth.currentUser == null) {
      await _auth.signInAnonymously();
    }

    startPeriodicSync();
    await syncAll();
  }

  /// Disable cloud sync
  Future<void> disableCloudSync() async {
    stopPeriodicSync();
  }

  /// Clear all cloud data
  Future<void> clearCloudData() async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      // Delete all tabs
      final tabsSnapshot = await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('tabs')
          .get();

      for (final doc in tabsSnapshot.docs) {
        await doc.reference.delete();
      }

      // Delete all groups
      final groupsSnapshot = await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('groups')
          .get();

      for (final doc in groupsSnapshot.docs) {
        await doc.reference.delete();
      }

      print('Cleared all cloud data');
    } catch (e) {
      print('Error clearing cloud data: $e');
      rethrow;
    }
  }

  /// Get last sync timestamp
  Future<DateTime?> getLastSyncTime() async {
    final user = _auth.currentUser;
    if (user == null) return null;

    try {
      final doc = await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('metadata')
          .doc('sync')
          .get();

      if (!doc.exists) return null;

      final timestamp = doc.data()?['lastSync'] as Timestamp?;
      return timestamp?.toDate();
    } catch (e) {
      print('Error getting last sync time: $e');
      return null;
    }
  }

  /// Update last sync timestamp
  Future<void> updateLastSyncTime() async {
    final user = _auth.currentUser;
    if (user == null) return;

    try {
      await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('metadata')
          .doc('sync')
          .set({
        'lastSync': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    } catch (e) {
      print('Error updating last sync time: $e');
    }
  }

  /// Dispose resources
  void dispose() {
    stopPeriodicSync();
  }
}
