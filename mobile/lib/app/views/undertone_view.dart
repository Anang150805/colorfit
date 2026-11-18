import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile/app/controllers/undertone_controller.dart';
import 'package:mobile/app/core/constants.dart';
import 'package:mobile/app/core/theme.dart';

/// Halaman 2: Pemilihan Undertone Kulit (Warm, Cool, Neutral).
class UndertoneView extends GetView<UndertoneController> {
  const UndertoneView({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Pilih Undertone Kulit'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Kenali Karakteristik Kulitmu',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Pilih kategori undertone kulitmu berdasarkan panduan ciri urat nadi dan perhiasan di bawah ini:',
                style: TextStyle(
                  fontSize: 14,
                  color: theme.textTheme.bodyMedium?.color?.withOpacity(0.75),
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 20),
              // Daftar Kartu Undertone Reaktif
              Expanded(
                child: ListView(
                  children: [
                    _buildUndertoneCard(
                      context: context,
                      value: AppConstants.undertoneWarm,
                      title: 'Warm Undertone',
                      subTitle: 'Nuansa Hangat & Earthy',
                      description:
                          '• Urat nadi tampak kehijauan di bawah cahaya alami.\n'
                          '• Perhiasan emas tampak lebih serasi dan menyatu.\n'
                          '• Kulit mudah kecokelatan (tan) saat terpapar sinar matahari.',
                      colors: [const Color(0xFFCC4E2A), const Color(0xFFE1AD01), const Color(0xFF556B2F)],
                    ),
                    const SizedBox(height: 14),
                    _buildUndertoneCard(
                      context: context,
                      value: AppConstants.undertoneCool,
                      title: 'Cool Undertone',
                      subTitle: 'Nuansa Dingin & Jewel Tones',
                      description:
                          '• Urat nadi tampak kebiruan atau keunguan.\n'
                          '• Perhiasan perak/silver tampak memukau dan berkilau.\n'
                          '• Kulit cenderung mudah memerah atau terbakar sinar matahari.',
                      colors: [const Color(0xFF000080), const Color(0xFF008055), const Color(0xFF800020)],
                    ),
                    const SizedBox(height: 14),
                    _buildUndertoneCard(
                      context: context,
                      value: AppConstants.undertoneNeutral,
                      title: 'Neutral Undertone',
                      subTitle: 'Nuansa Seimbang & Muted',
                      description:
                          '• Urat nadi merupakan campuran antara kehijauan dan kebiruan.\n'
                          '• Terlihat serasi mengenakan perhiasan emas maupun perak.\n'
                          '• Sangat fleksibel dan anggun dengan warna-warna lembut (soft).',
                      colors: [const Color(0xFFDCAE96), const Color(0xFF9CAF88), const Color(0xFF36454F)],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              // Tombol Lanjutkan
              ElevatedButton(
                onPressed: controller.proceedToPalette,
                child: const Text('Lanjutkan ke Rekomendasi Warna'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUndertoneCard({
    required BuildContext context,
    required String value,
    required String title,
    required String subTitle,
    required String description,
    required List<Color> colors,
  }) {
    final theme = Theme.of(context);

    return Obx(() {
      final isSelected = controller.selectedUndertone.value == value;

      return InkWell(
        onTap: () => controller.selectUndertone(value),
        borderRadius: BorderRadius.circular(16),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isSelected
                ? AppTheme.primaryColor.withOpacity(0.08)
                : theme.cardTheme.color,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: isSelected ? AppTheme.primaryColor : theme.dividerColor.withOpacity(0.2),
              width: isSelected ? 2.0 : 1.0,
            ),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: AppTheme.primaryColor.withOpacity(0.15),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    )
                  ]
                : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // Radio Indicator
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: isSelected ? AppTheme.primaryColor : Colors.grey,
                        width: 2,
                      ),
                    ),
                    child: isSelected
                        ? Center(
                            child: Container(
                              width: 12,
                              height: 12,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: AppTheme.primaryColor,
                              ),
                            ),
                          )
                        : null,
                  ),
                  const SizedBox(width: 12),
                  // Judul Kartu
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: isSelected ? AppTheme.primaryColor : null,
                          ),
                        ),
                        Text(
                          subTitle,
                          style: TextStyle(
                            fontSize: 12,
                            color: theme.textTheme.bodyMedium?.color?.withOpacity(0.6),
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Dot Palet Karakteristik
                  Row(
                    children: colors.map((c) {
                      return Container(
                        margin: const EdgeInsets.only(left: 4),
                        width: 16,
                        height: 16,
                        decoration: BoxDecoration(
                          color: c,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 1.5),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              // Deskripsi Ciri Kulit
              Text(
                description,
                style: TextStyle(
                  fontSize: 13,
                  height: 1.45,
                  color: theme.textTheme.bodyMedium?.color?.withOpacity(0.85),
                ),
              ),
            ],
          ),
        ),
      );
    });
  }
}
