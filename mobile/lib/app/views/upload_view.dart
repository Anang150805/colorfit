import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile/app/controllers/upload_controller.dart';
import 'package:mobile/app/core/theme.dart';

/// Halaman 5: Unggah Foto dari Galeri.
class UploadView extends GetView<UploadController> {
  const UploadView({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Unggah Foto Pakaian'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Obx(() {
            final bytes = controller.imageBytes.value;

            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Pratinjau Foto Pakaian',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Pastikan foto memiliki pencahayaan cukup dan warna pakaian terlihat jelas.',
                  style: TextStyle(
                    fontSize: 13,
                    color: theme.textTheme.bodyMedium?.color?.withOpacity(0.7),
                  ),
                ),
                const SizedBox(height: 20),
                // Area Pratinjau Gambar
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: theme.dividerColor.withOpacity(0.2),
                        width: 1.5,
                      ),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: bytes != null
                        ? Stack(
                            fit: StackFit.expand,
                            children: [
                              Image.memory(
                                bytes,
                                fit: BoxFit.contain,
                              ),
                              Positioned(
                                top: 12,
                                right: 12,
                                child: CircleAvatar(
                                  backgroundColor: Colors.black54,
                                  child: IconButton(
                                    icon: const Icon(Icons.edit, color: Colors.white, size: 20),
                                    tooltip: 'Ganti Foto',
                                    onPressed: controller.pickImageFromGallery,
                                  ),
                                ),
                              ),
                            ],
                          )
                        : InkWell(
                            onTap: controller.pickImageFromGallery,
                            child: const Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.add_photo_alternate_outlined,
                                    size: 64,
                                    color: Colors.grey,
                                  ),
                                  SizedBox(height: 12),
                                  Text(
                                    'Ketuk untuk memilih foto pakaian',
                                    style: TextStyle(
                                      color: Colors.grey,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                  ),
                ),
                if (controller.errorMessage.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: Colors.red, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            controller.errorMessage.value,
                            style: TextStyle(color: Colors.red.shade900, fontSize: 12),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 20),
                // Tombol Aksi
                if (bytes != null) ...[
                  ElevatedButton.icon(
                    onPressed: controller.isAnalyzing.value ? null : controller.analyzeSelectedImage,
                    icon: controller.isAnalyzing.value
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5),
                          )
                        : const Icon(Icons.auto_awesome),
                    label: Text(
                      controller.isAnalyzing.value ? 'Menganalisis Pakaian...' : 'Analisis Pakaian',
                    ),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton(
                    onPressed: controller.isAnalyzing.value ? null : controller.pickImageFromGallery,
                    child: const Text('Pilih Foto Lain'),
                  ),
                ] else ...[
                  ElevatedButton.icon(
                    onPressed: controller.pickImageFromGallery,
                    icon: const Icon(Icons.photo_library_outlined),
                    label: const Text('Buka Galeri Foto'),
                  ),
                ],
              ],
            );
          }),
        ),
      ),
    );
  }
}
