import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import 'package:get/get.dart';
import 'package:mobile/app/models/history_item.dart';
import 'package:mobile/app/services/device_id_service.dart';

/// Service untuk menyimpan dan membaca riwayat analisis pakaian di Cloud Firestore.
/// Struktur Firestore:
///   dokumen:   devices/{device_id}           → field undertone, updatedAt
///   koleksi:   devices/{device_id}/histories/{id}
///
/// Jika Firebase belum dikonfigurasi, service berjalan dalam mode fallback
/// lokal (in-memory) tanpa menyebabkan crash.
class FirestoreService extends GetxService {
  final bool isFirebaseAvailable;
  FirebaseFirestore? _firestore;

  // Cache lokal sementara jika Firebase belum aktif
  final RxList<HistoryItem> _localHistories = <HistoryItem>[].obs;

  FirestoreService(this.isFirebaseAvailable);

  @override
  void onInit() {
    super.onInit();
    if (isFirebaseAvailable) {
      try {
        _firestore = FirebaseFirestore.instance;
      } catch (e) {
        debugPrint('[FirestoreService] Gagal inisialisasi Firestore: $e');
      }
    }
  }

  /// Referensi koleksi histories perangkat aktif: devices/{device_id}/histories
  CollectionReference<Map<String, dynamic>>? _historiesCollection() {
    if (!isFirebaseAvailable || _firestore == null) return null;
    final deviceId = Get.find<DeviceIdService>().deviceId;
    return _firestore!.collection('devices').doc(deviceId).collection('histories');
  }

  /// Memperbarui/membuat dokumen devices/{device_id} dengan undertone & timestamp.
  /// Dipanggil setiap kali pengguna memilih undertone di UndertoneController.
  Future<void> updateDeviceUndertone(String undertone) async {
    if (!isFirebaseAvailable || _firestore == null) {
      debugPrint('[FirestoreService] Firebase tidak aktif; undertone tidak disimpan ke cloud.');
      return;
    }
    try {
      final deviceId = Get.find<DeviceIdService>().deviceId;
      await _firestore!.collection('devices').doc(deviceId).set(
        {
          'undertone': undertone,
          'updatedAt': FieldValue.serverTimestamp(),
        },
        SetOptions(merge: true),
      );
    } catch (e) {
      debugPrint('[FirestoreService] Gagal memperbarui undertone di Firestore: $e');
    }
  }

  /// Menyimpan riwayat analisis baru ke Firestore.
  Future<void> saveHistory(HistoryItem item) async {
    // Simpan ke cache lokal agar langsung terlihat di UI
    _localHistories.insert(0, item);

    if (!isFirebaseAvailable || _firestore == null) {
      debugPrint(
        '[FirestoreService] Firebase belum aktif. Riwayat disimpan di memori sementara. '
        'Jalankan `flutterfire configure` untuk mengaktifkan sinkronisasi cloud.',
      );
      return;
    }

    try {
      final collection = _historiesCollection();
      if (collection != null) {
        await collection.add(item.toMap(useServerTimestamp: true));
      }
    } catch (e) {
      debugPrint('[FirestoreService] Gagal menyimpan ke Firestore: $e');
    }
  }

  /// Stream riwayat pemindaian untuk perangkat aktif (real-time).
  Stream<List<HistoryItem>> streamHistories() {
    final collection = _historiesCollection();
    if (collection == null) {
      return _localHistories.stream;
    }

    return collection
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs
          .map((doc) => HistoryItem.fromMap(doc.data(), doc.id))
          .toList();
    });
  }

  /// Mengambil daftar riwayat satu kali (Future).
  Future<List<HistoryItem>> fetchHistories() async {
    final collection = _historiesCollection();
    if (collection == null) {
      return List<HistoryItem>.from(_localHistories);
    }

    try {
      final querySnapshot = await collection
          .orderBy('createdAt', descending: true)
          .get();
      return querySnapshot.docs
          .map((doc) => HistoryItem.fromMap(doc.data(), doc.id))
          .toList();
    } catch (e) {
      debugPrint('[FirestoreService] Gagal mengambil riwayat: $e');
      return List<HistoryItem>.from(_localHistories);
    }
  }
}
