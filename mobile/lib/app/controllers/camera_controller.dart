import 'dart:async';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image/image.dart' as img;

import 'package:mobile/app/core/constants.dart';
import 'package:mobile/app/routes/app_routes.dart';
import 'package:mobile/app/services/api_service.dart';

// ---------------------------------------------------------------------------
// Fungsi top-level untuk compute() – harus berada di luar class
// Menerima Map dengan kunci 'planes', 'width', 'height', 'maxWidth'
// Mengembalikan Uint8List JPEG atau null jika gagal konversi
// ---------------------------------------------------------------------------
Uint8List? _convertYuvToJpeg(Map<String, dynamic> args) {
  try {
    final int width = args['width'] as int;
    final int height = args['height'] as int;
    final int maxWidth = args['maxWidth'] as int;

    // planes: List<Map> masing-masing dengan 'bytes', 'bytesPerRow', 'bytesPerPixel'
    final List<dynamic> planes = args['planes'] as List<dynamic>;
    final Uint8List yBytes = planes[0]['bytes'] as Uint8List;
    final Uint8List uBytes = planes[1]['bytes'] as Uint8List;
    final Uint8List vBytes = planes[2]['bytes'] as Uint8List;
    final int uvRowStride = planes[1]['bytesPerRow'] as int;
    final int uvPixelStride = planes[1]['bytesPerPixel'] as int;

    // Buat image RGB dari YUV420
    final image = img.Image(width: width, height: height);
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final int uvIndex = uvPixelStride * (x ~/ 2) + uvRowStride * (y ~/ 2);
        final int yVal = yBytes[y * width + x];
        final int uVal = uBytes[uvIndex];
        final int vVal = vBytes[uvIndex];

        // YUV → RGB
        int r = (yVal + 1.370705 * (vVal - 128)).round().clamp(0, 255);
        int g = (yVal - 0.337633 * (uVal - 128) - 0.698001 * (vVal - 128)).round().clamp(0, 255);
        int b = (yVal + 1.732446 * (uVal - 128)).round().clamp(0, 255);
        image.setPixelRgb(x, y, r, g, b);
      }
    }

    // Resize ke lebar maks agar payload kecil
    final img.Image resized = width > maxWidth
        ? img.copyResize(image, width: maxWidth)
        : image;

    return Uint8List.fromList(img.encodeJpg(resized, quality: 70));
  } catch (e) {
    return null;
  }
}

/// Controller untuk Halaman Scan Kamera Real-Time (ColorFit Camera).
/// Menggunakan startImageStream agar tidak ada suara rana atau kedip layar.
class CameraScanController extends GetxController with WidgetsBindingObserver {
  final ApiService _apiService = Get.find<ApiService>();

  CameraController? cameraController;
  final RxBool isCameraInitialized = false.obs;
  final RxBool hasPermission = true.obs;
  final RxBool isFlashOn = false.obs;
  final RxBool isAnalyzing = false.obs;
  final RxString detectedHex = '#FFFFFF'.obs;
  final RxString errorMessage = ''.obs;

  String undertone = AppConstants.undertoneWarm;

  /// Throttle: waktu frame terakhir yang diproses
  DateTime _lastFrameTime = DateTime.fromMillisecondsSinceEpoch(0);

  /// Mencegah dua permintaan /api/detect berjalan bersamaan
  bool _isDetecting = false;

  // ---------------------------------------------------------------------------
  // Lifecycle
  // ---------------------------------------------------------------------------

  @override
  void onInit() {
    super.onInit();
    WidgetsBinding.instance.addObserver(this);

    final args = Get.arguments as Map<String, dynamic>?;
    if (args != null && args.containsKey('undertone')) {
      undertone = args['undertone'].toString();
    }
    initCamera();
  }

  @override
  void onClose() {
    WidgetsBinding.instance.removeObserver(this);
    _stopStream();
    cameraController?.dispose();
    super.onClose();
  }

  /// Hentikan stream saat app masuk background, lanjutkan saat foreground
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final cc = cameraController;
    if (cc == null || !cc.value.isInitialized) return;

    if (state == AppLifecycleState.inactive || state == AppLifecycleState.paused) {
      _stopStream();
    } else if (state == AppLifecycleState.resumed) {
      _startStream();
    }
  }

  // ---------------------------------------------------------------------------
  // Inisialisasi Kamera
  // ---------------------------------------------------------------------------

  /// Menginisialisasi kamera. Izin kamera diminta otomatis oleh package camera.
  Future<void> initCamera() async {
    errorMessage.value = '';
    hasPermission.value = true;
    isCameraInitialized.value = false;

    try {
      // Bersihkan controller lama bila dipanggil ulang (tombol Coba Lagi)
      await cameraController?.dispose();
      cameraController = null;

      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        errorMessage.value = 'Tidak ada kamera yang terdeteksi pada perangkat ini.';
        return;
      }

      final backCamera = cameras.firstWhere(
        (cam) => cam.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      // Gunakan low/medium untuk performa stream yang baik
      cameraController = CameraController(
        backCamera,
        ResolutionPreset.low,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420,
      );

      await cameraController!.initialize();
      isCameraInitialized.value = true;

      // Mulai stream frame YUV420
      _startStream();
    } on CameraException catch (e) {
      if (e.code == 'CameraAccessDenied' ||
          e.code == 'CameraAccessDeniedWithoutPrompt' ||
          e.code == 'CameraAccessRestricted') {
        hasPermission.value = false;
        errorMessage.value =
            'Izin kamera ditolak. Aktifkan izin kamera untuk ColorFit di Pengaturan HP, lalu tekan Coba Lagi.';
      } else {
        errorMessage.value = 'Gagal menyiapkan kamera: ${e.description ?? e.code}';
      }
    } catch (e) {
      errorMessage.value = 'Gagal menyiapkan kamera: $e';
    }
  }

  // ---------------------------------------------------------------------------
  // Image Stream
  // ---------------------------------------------------------------------------

  void _startStream() {
    final cc = cameraController;
    if (cc == null || !cc.value.isInitialized) return;
    if (cc.value.isStreamingImages) return;

    cc.startImageStream(_onFrame);
  }

  void _stopStream() {
    final cc = cameraController;
    if (cc == null || !cc.value.isInitialized) return;
    if (!cc.value.isStreamingImages) return;

    try {
      cc.stopImageStream();
    } catch (_) {}
  }

  /// Callback dipanggil tiap frame dari kamera
  void _onFrame(CameraImage frame) {
    // Lewati jika sedang menganalisis foto penuh
    if (isAnalyzing.value) return;

    // Throttle: hanya proses satu frame per detik
    final now = DateTime.now();
    if (now.difference(_lastFrameTime).inMilliseconds < 1000) return;

    // Lewati jika permintaan sebelumnya belum selesai
    if (_isDetecting) return;

    _lastFrameTime = now;
    _isDetecting = true;

    // Jalankan konversi YUV→JPEG di isolate agar UI tidak tersendat
    _processFrameInBackground(frame).then((hex) {
      if (hex != null) detectedHex.value = hex;
    }).whenComplete(() {
      _isDetecting = false;
    });
  }

  Future<String?> _processFrameInBackground(CameraImage frame) async {
    try {
      // Siapkan data yang bisa dikirim ke isolate (tidak boleh ada object Flutter)
      final planeData = frame.planes.map((p) => {
        'bytes': p.bytes,
        'bytesPerRow': p.bytesPerRow,
        'bytesPerPixel': p.bytesPerPixel ?? 1,
      }).toList();

      final args = {
        'planes': planeData,
        'width': frame.width,
        'height': frame.height,
        'maxWidth': 160, // resize ke 160px lebar
      };

      final jpegBytes = await compute(_convertYuvToJpeg, args);
      if (jpegBytes == null || jpegBytes.isEmpty) return null;

      final hex = await _apiService.detect(jpegBytes);
      return hex;
    } catch (e) {
      debugPrint('[CameraScanController] Frame dilewati: $e');
      return null;
    }
  }

  // ---------------------------------------------------------------------------
  // Flash
  // ---------------------------------------------------------------------------

  /// Toggle lampu senter (Torch)
  Future<void> toggleFlash() async {
    final cc = cameraController;
    if (cc == null || !cc.value.isInitialized) return;

    try {
      if (isFlashOn.value) {
        await cc.setFlashMode(FlashMode.off);
        isFlashOn.value = false;
      } else {
        await cc.setFlashMode(FlashMode.torch);
        isFlashOn.value = true;
      }
    } catch (e) {
      debugPrint('[CameraScanController] Gagal mengatur flash: $e');
    }
  }

  // ---------------------------------------------------------------------------
  // Capture & Analyze
  // ---------------------------------------------------------------------------

  /// Hentikan stream, ambil foto penuh, kirim ke POST /api/analyze
  Future<void> captureAndAnalyze() async {
    final cc = cameraController;
    if (cc == null || !cc.value.isInitialized || isAnalyzing.value) return;

    isAnalyzing.value = true;

    // Hentikan stream sebelum takePicture
    _stopStream();

    try {
      final xFile = await cc.takePicture();
      final bytes = await xFile.readAsBytes();

      final result = await _apiService.analyze(
        bytes,
        undertone,
        filename: 'scan_clothing.jpg',
      );

      // Navigasi ke halaman hasil
      Get.toNamed(
        Routes.RESULT,
        arguments: {
          'analyzeResult': result,
          'undertone': undertone,
        },
      );
    } catch (e) {
      Get.snackbar(
        'Gagal Analisis',
        e.toString(),
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: const Color(0xFFD32F2F),
        colorText: const Color(0xFFFFFFFF),
        duration: const Duration(seconds: 4),
      );
      // Lanjutkan stream jika analisis gagal
      _startStream();
    } finally {
      isAnalyzing.value = false;
    }
  }
}