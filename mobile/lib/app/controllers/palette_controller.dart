import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/app/core/constants.dart';
import 'package:mobile/app/models/color_result.dart';
import 'package:mobile/app/routes/app_routes.dart';
import 'package:mobile/app/services/api_service.dart';

/// Controller untuk halaman Rekomendasi Palet Warna (/api/classify).
class PaletteController extends GetxController {
  final ApiService _apiService = Get.find<ApiService>();
  final SharedPreferences _prefs = Get.find<SharedPreferences>();

  final RxString undertone = AppConstants.undertoneWarm.obs;
  final RxBool isLoading = true.obs;
  final RxString errorMessage = ''.obs;

  final RxList<ColorItem> allColors = <ColorItem>[].obs;
  final RxString selectedFamilyFilter = 'Semua'.obs;

  final List<String> availableFamilies = [
    'Semua',
    'merah',
    'kuning',
    'hijau',
    'biru',
    'ungu',
    'oranye',
    'pink',
    'coklat',
    'netral'
  ];

  @override
  void onInit() {
    super.onInit();
    final args = Get.arguments as Map<String, dynamic>?;
    if (args != null && args.containsKey('undertone')) {
      undertone.value = args['undertone'].toString();
    } else {
      undertone.value = _prefs.getString(AppConstants.keySelectedUndertone) ?? AppConstants.undertoneWarm;
    }
    fetchPalette();
  }

  Future<void> fetchPalette() async {
    isLoading.value = true;
    errorMessage.value = '';

    try {
      final result = await _apiService.classify(undertone.value);
      allColors.assignAll(result.colors);
    } catch (e) {
      errorMessage.value = e.toString();
    } finally {
      isLoading.value = false;
    }
  }

  void filterFamily(String family) {
    selectedFamilyFilter.value = family;
  }

  List<ColorItem> get filteredColors {
    if (selectedFamilyFilter.value == 'Semua') {
      return allColors;
    }
    return allColors
        .where((c) => c.family.toLowerCase() == selectedFamilyFilter.value.toLowerCase())
        .toList();
  }

  /// Navigasi ke Halaman Pemindaian Kamera
  void openCameraScanner() {
    Get.toNamed(
      Routes.CAMERA,
      arguments: {'undertone': undertone.value},
    );
  }

  /// Navigasi ke Halaman Unggah Galeri
  void openGalleryUpload() {
    Get.toNamed(
      Routes.UPLOAD,
      arguments: {'undertone': undertone.value},
    );
  }
}
