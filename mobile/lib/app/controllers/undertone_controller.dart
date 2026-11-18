import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/app/core/constants.dart';
import 'package:mobile/app/routes/app_routes.dart';
import 'package:mobile/app/services/firestore_service.dart';

/// Controller untuk halaman pemilihan Undertone Kulit.
class UndertoneController extends GetxController {
  final SharedPreferences _prefs = Get.find<SharedPreferences>();
  final FirestoreService _firestoreService = Get.find<FirestoreService>();

  // Undertone terpilih secara reaktif
  final RxString selectedUndertone = AppConstants.undertoneWarm.obs;

  @override
  void onInit() {
    super.onInit();
    // Muat preferensi undertone sebelumnya jika ada
    final saved = _prefs.getString(AppConstants.keySelectedUndertone);
    if (saved != null && saved.isNotEmpty) {
      selectedUndertone.value = saved;
    }
  }

  void selectUndertone(String undertone) {
    selectedUndertone.value = undertone;
  }

  Future<void> proceedToPalette() async {
    // 1. Simpan ke SharedPreferences (lokal, offline-first)
    await _prefs.setString(AppConstants.keySelectedUndertone, selectedUndertone.value);

    // 2. Simpan ke Firestore: devices/{device_id} → {undertone, updatedAt}
    //    Gagal diam-diam jika Firebase belum aktif
    _firestoreService.updateDeviceUndertone(selectedUndertone.value);

    // 3. Navigasi ke Rekomendasi Palet Warna
    Get.toNamed(
      Routes.PALETTE,
      arguments: {'undertone': selectedUndertone.value},
    );
  }
}
