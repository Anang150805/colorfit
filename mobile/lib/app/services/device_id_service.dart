import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import 'package:mobile/app/core/constants.dart';

/// Service untuk mengelola pengenal perangkat unik (Device ID).
/// Dibuat sekali dengan UUID v4 pada peluncuran pertama, disimpan di SharedPreferences,
/// dan digunakan seterusnya sebagai identitas koleksi Firestore: devices/{device_id}/histories.
class DeviceIdService extends GetxService {
  final SharedPreferences _prefs;
  late final String deviceId;

  DeviceIdService(this._prefs);

  @override
  void onInit() {
    super.onInit();
    deviceId = _getOrCreateDeviceId();
  }

  String _getOrCreateDeviceId() {
    String? existing = _prefs.getString(AppConstants.keyDeviceId);
    if (existing == null || existing.trim().isEmpty) {
      existing = const Uuid().v4();
      _prefs.setString(AppConstants.keyDeviceId, existing);
    }
    return existing;
  }
}
