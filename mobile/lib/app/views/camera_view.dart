import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'package:mobile/app/controllers/camera_controller.dart';
import 'package:mobile/app/core/theme.dart';
import 'package:mobile/app/core/utils.dart';

/// Halaman 4: Scan Kamera Real-Time dengan panduan bingkai pakaian dan deteksi HEX instan.
class CameraView extends GetView<CameraScanController> {
  const CameraView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Obx(() {
          // State: error kamera (izin ditolak atau kamera gagal)
          if (controller.errorMessage.isNotEmpty) {
            return _buildPermissionDeniedState();
          }

          // State: kamera belum siap
          if (!controller.isCameraInitialized.value) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Colors.white),
                  SizedBox(height: 16),
                  Text(
                    'Menyiapkan kamera...',
                    style: TextStyle(color: Colors.white70),
                  ),
                ],
              ),
            );
          }

          // State: kamera aktif
          return Stack(
            fit: StackFit.expand,
            children: [
              // 1. Pratinjau Kamera Penuh
              Center(
                child: CameraPreview(controller.cameraController!),
              ),

              // 2. Panduan Bingkai Pakaian
              _buildClothingFrameOverlay(context),

              // 3. Bar Kontrol Atas (Kembali & Flash)
              Positioned(
                top: 16,
                left: 16,
                right: 16,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    CircleAvatar(
                      backgroundColor: Colors.black45,
                      child: IconButton(
                        icon: const Icon(Icons.arrow_back, color: Colors.white),
                        onPressed: () => Get.back(),
                      ),
                    ),
                    Obx(() {
                      return CircleAvatar(
                        backgroundColor:
                            controller.isFlashOn.value ? AppTheme.accentColor : Colors.black45,
                        child: IconButton(
                          icon: Icon(
                            controller.isFlashOn.value ? Icons.flash_on : Icons.flash_off,
                            color: Colors.white,
                          ),
                          onPressed: controller.toggleFlash,
                        ),
                      );
                    }),
                  ],
                ),
              ),

              // 4. Badge Deteksi Warna Real-Time
              Positioned(
                top: 80,
                left: 32,
                right: 32,
                child: _buildLiveColorBadge(),
              ),

              // 5. Tombol Shutter
              Positioned(
                bottom: 30,
                left: 0,
                right: 0,
                child: _buildShutterControls(),
              ),

              // 6. Loading Overlay saat analisis berlangsung
              Obx(() {
                if (!controller.isAnalyzing.value) return const SizedBox.shrink();
                return Container(
                  color: Colors.black54,
                  child: const Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(color: Colors.white),
                        SizedBox(height: 20),
                        Text(
                          'Menganalisis harmoni pakaian...',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ],
          );
        }),
      ),
    );
  }

  Widget _buildClothingFrameOverlay(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final boxW = constraints.maxWidth * 0.75;
        final boxH = constraints.maxHeight * 0.45;

        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: boxW,
                height: boxH,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: Colors.white.withOpacity(0.8),
                    width: 2.5,
                  ),
                ),
                child: Center(
                  child: Icon(
                    Icons.crop_free,
                    size: 40,
                    color: Colors.white.withOpacity(0.4),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  'Arahkan kamera ke bagian utama pakaian',
                  style: TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildLiveColorBadge() {
    return Obx(() {
      final hex = controller.detectedHex.value;
      final color = AppUtils.hexToColor(hex);

      return Center(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.black87,
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: Colors.white24),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 10,
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                'Terdeteksi: $hex',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
        ),
      );
    });
  }

  Widget _buildShutterControls() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: controller.captureAndAnalyze,
          child: Container(
            width: 76,
            height: 76,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 4),
            ),
            child: Center(
              child: Container(
                width: 60,
                height: 60,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 10),
        const Text(
          'Ketuk untuk Menganalisis',
          style: TextStyle(
            color: Colors.white70,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  /// State error kamera (izin ditolak atau kamera gagal) dengan tombol Coba Lagi
  Widget _buildPermissionDeniedState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.no_photography_outlined, size: 64, color: Colors.white54),
            const SizedBox(height: 16),
            Obx(() => Text(
                  controller.errorMessage.value,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                )),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.refresh),
              label: const Text('Coba Lagi'),
              onPressed: controller.initCamera,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.accentColor,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: () => Get.back(),
              child: const Text(
                'Kembali',
                style: TextStyle(color: Colors.white70),
              ),
            ),
          ],
        ),
      ),
    );
  }
}