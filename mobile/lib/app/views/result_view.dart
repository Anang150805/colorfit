import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile/app/controllers/result_controller.dart';
import 'package:mobile/app/core/theme.dart';
import 'package:mobile/app/core/utils.dart';
import 'package:mobile/app/widgets/harmony_card.dart';
import 'package:mobile/app/widgets/suitability_badge.dart';

/// Halaman 6: Hasil Rekomendasi Padu-Padan Pakaian (ColorFit Analysis).
class ResultView extends GetView<ResultController> {
  const ResultView({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hasil Analisis Pakaian'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: controller.retakePhoto,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history_rounded),
            tooltip: 'Riwayat',
            onPressed: controller.openHistory,
          ),
        ],
      ),
      body: SafeArea(
        child: Obx(() {
          final res = controller.result.value;

          // State Gagal / Data Tidak Valid
          if (res == null || !res.success || res.detected == null) {
            return _buildErrorState(context, res?.message);
          }

          final detected = res.detected!;
          final detectedColor = AppUtils.hexToColor(detected.hex);

          return SingleChildScrollView(
            padding: const EdgeInsets.only(bottom: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1. Kartu Warna Pakaian Terdeteksi & Kesesuaian
                Container(
                  margin: const EdgeInsets.all(16),
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: theme.cardTheme.color,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      // Lingkaran Swatch Utama
                      Container(
                        width: 90,
                        height: 90,
                        decoration: BoxDecoration(
                          color: detectedColor,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.black12, width: 3),
                          boxShadow: [
                            BoxShadow(
                              color: detectedColor.withOpacity(0.35),
                              blurRadius: 14,
                              offset: const Offset(0, 6),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        detected.hex.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'monospace',
                        ),
                      ),
                      const SizedBox(height: 8),
                      // Badge Kesesuaian
                      SuitabilityBadge(
                        suitability: res.suitability,
                        isLarge: true,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Kesesuaian dengan ${controller.undertone.value.capitalizeFirst} Undertone',
                        style: TextStyle(
                          fontSize: 12,
                          color: theme.textTheme.bodyMedium?.color?.withOpacity(0.6),
                        ),
                      ),
                      const Divider(height: 24),
                      // Rincian Ruang Warna Lengkap (RGB, HSV, CIELAB)
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildColorSpecItem('RGB', '${detected.rgb[0]}, ${detected.rgb[1]}, ${detected.rgb[2]}'),
                          _buildColorSpecItem('HSV', '${detected.hsv[0].toStringAsFixed(0)}°, ${(detected.hsv[1] * 100).toStringAsFixed(0)}%, ${(detected.hsv[2] * 100).toStringAsFixed(0)}%'),
                          _buildColorSpecItem('CIELAB', 'L:${detected.lab[0].toStringAsFixed(0)} a:${detected.lab[1].toStringAsFixed(0)} b:${detected.lab[2].toStringAsFixed(0)}'),
                        ],
                      ),
                    ],
                  ),
                ),

                // 2. Judul Bagian Rekomendasi Paduan Pakaian
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                  child: Row(
                    children: [
                      const Icon(Icons.style, size: 20, color: AppTheme.primaryColor),
                      const SizedBox(width: 8),
                      Text(
                        'Rekomendasi Paduan Serasi (KNN & Itten)',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

                // 3. Daftar HarmonyCard
                if (res.recommendations.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Center(
                      child: Text('Tidak ada rekomendasi pakaian serasi yang ditemukan.'),
                    ),
                  )
                else
                  ...res.recommendations.map(
                    (rec) => HarmonyCard(recommendation: rec),
                  ),

                const SizedBox(height: 20),

                // 4. Tombol Aksi Bawah
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: controller.retakePhoto,
                          icon: const Icon(Icons.camera_alt_outlined),
                          label: const Text('Ambil Ulang'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: controller.backToHome,
                          icon: const Icon(Icons.home_outlined),
                          label: const Text('Beranda'),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _buildColorSpecItem(String label, String value) {
    return Column(
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.bold,
            color: Colors.grey,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(
            fontSize: 12,
            fontFamily: 'monospace',
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildErrorState(BuildContext context, String? message) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.warning_amber_rounded,
              size: 64,
              color: Colors.orange,
            ),
            const SizedBox(height: 16),
            const Text(
              'Analisis Pakaian Tidak Berhasil',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              message ??
                  'Warna pakaian tidak dapat dideteksi dengan jelas (terlalu gelap, silau, atau objek tidak berada di tengah). Silakan ambil ulang gambar dengan pencahayaan yang cukup.',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: controller.retakePhoto,
              icon: const Icon(Icons.refresh),
              label: const Text('Ambil Ulang Foto'),
            ),
          ],
        ),
      ),
    );
  }
}
