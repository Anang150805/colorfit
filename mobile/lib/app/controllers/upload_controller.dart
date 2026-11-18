import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile/app/core/constants.dart';
import 'package:mobile/app/routes/app_routes.dart';
import 'package:mobile/app/services/api_service.dart';

/// Controller untuk Halaman Unggah Foto dari Galeri.
class UploadController extends GetxController {
  final ApiService _apiService = Get.find<ApiService>();
  final ImagePicker _picker = ImagePicker();

  final Rx<XFile?> selectedFile = Rx<XFile?>(null);
  final Rx<Uint8List?> imageBytes = Rx<Uint8List?>(null);

  final RxBool isAnalyzing = false.obs;
  final RxString errorMessage = ''.obs;

  String undertone = AppConstants.undertoneWarm;

  @override
  void onInit() {
    super.onInit();
    final args = Get.arguments as Map<String, dynamic>?;
    if (args != null && args.containsKey('undertone')) {
      undertone = args['undertone'].toString();
    }
    // Langsung buka pemilih galeri saat halaman pertama kali dibuka
    pickImageFromGallery();
  }

  /// Memilih foto pakaian dari galeri dengan validasi ekstensi dan kompresi
  Future<void> pickImageFromGallery() async {
    errorMessage.value = '';
    try {
      final XFile? file = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1080,   // Lebar maks agar upload ringan
        imageQuality: 85, // Kompresi JPEG ringan
      );

      if (file == null) return; // Pengguna membatalkan

      // Validasi ekstensi: hanya JPG dan PNG yang didukung
      final ext = file.name.toLowerCase();
      final isJpg = ext.endsWith('.jpg') || ext.endsWith('.jpeg');
      final isPng = ext.endsWith('.png');
      if (!isJpg && !isPng) {
        errorMessage.value = 'Hanya file JPG atau PNG yang didukung. '
            'Silakan pilih gambar dengan format yang benar.';
        return;
      }

      selectedFile.value = file;
      final bytes = await file.readAsBytes();
      imageBytes.value = bytes;
    } catch (e) {
      errorMessage.value = 'Gagal memilih gambar dari galeri: $e';
    }
  }

  /// Memanggil POST /api/analyze untuk gambar yang dipilih
  Future<void> analyzeSelectedImage() async {
    final bytes = imageBytes.value;
    final file = selectedFile.value;

    if (bytes == null || file == null) {
      errorMessage.value = 'Silakan pilih foto pakaian terlebih dahulu.';
      return;
    }

    isAnalyzing.value = true;
    errorMessage.value = '';

    try {
      final result = await _apiService.analyze(
        bytes,
        undertone,
        filename: file.name,
      );

      Get.toNamed(
        Routes.RESULT,
        arguments: {
          'analyzeResult': result,
          'undertone': undertone,
        },
      );
    } catch (e) {
      errorMessage.value = e.toString();
      Get.snackbar(
        'Analisis Gagal',
        e.toString(),
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: const Color(0xFFD32F2F),
        colorText: Colors.white,
        duration: const Duration(seconds: 4),
      );
    } finally {
      isAnalyzing.value = false;
    }
  }
}
