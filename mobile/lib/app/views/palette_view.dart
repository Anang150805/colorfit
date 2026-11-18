import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile/app/controllers/palette_controller.dart';
import 'package:mobile/app/core/theme.dart';
import 'package:mobile/app/widgets/color_chip.dart';
import 'package:mobile/app/widgets/suitability_badge.dart';

/// Halaman 3: Rekomendasi Palet Warna Kulit & Pintu Masuk Pencocokan Pakaian.
class PaletteView extends GetView<PaletteController> {
  const PaletteView({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text('Palet ${controller.undertone.value.capitalizeFirst}')),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Muat Ulang',
            onPressed: controller.fetchPalette,
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Filter Bar Kategori Family Warna
            _buildFamilyFilterBar(theme),

            // Konten Palet Warna
            Expanded(
              child: Obx(() {
                if (controller.isLoading.value) {
                  return const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text('Menghitung kesesuaian warna via Decision Tree...'),
                      ],
                    ),
                  );
                }

                if (controller.errorMessage.isNotEmpty) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.error_outline, size: 48, color: Colors.red),
                          const SizedBox(height: 16),
                          Text(
                            controller.errorMessage.value,
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 14),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: controller.fetchPalette,
                            icon: const Icon(Icons.refresh),
                            label: const Text('Coba Lagi'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                final colors = controller.filteredColors;
                if (colors.isEmpty) {
                  return const Center(
                    child: Text('Tidak ada warna dalam rumpun ini.'),
                  );
                }

                return ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  itemCount: colors.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final item = colors[index];
                    return Card(
                      elevation: 0.8,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        child: Row(
                          children: [
                            ColorChipWidget(
                              hex: item.hex,
                              name: item.name,
                              size: 40,
                            ),
                            const Spacer(),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                SuitabilityBadge(suitability: item.suitability),
                                const SizedBox(height: 4),
                                Text(
                                  item.family.toUpperCase(),
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.grey.shade600,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              }),
            ),

            // Bottom Bar: Pilihan Sumber Gambar Pakaian
            _buildBottomActionBar(context),
          ],
        ),
      ),
    );
  }

  Widget _buildFamilyFilterBar(ThemeData theme) {
    return Container(
      height: 52,
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        border: Border(
          bottom: BorderSide(
            color: theme.dividerColor.withOpacity(0.15),
          ),
        ),
      ),
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        scrollDirection: Axis.horizontal,
        itemCount: controller.availableFamilies.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final family = controller.availableFamilies[index];
          return Obx(() {
            final isSelected = controller.selectedFamilyFilter.value == family;
            return ChoiceChip(
              label: Text(family.capitalizeFirst ?? family),
              selected: isSelected,
              onSelected: (_) => controller.filterFamily(family),
              selectedColor: AppTheme.primaryColor.withOpacity(0.15),
              labelStyle: TextStyle(
                color: isSelected ? AppTheme.primaryColor : null,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                fontSize: 12,
              ),
              side: BorderSide(
                color: isSelected ? AppTheme.primaryColor : Colors.grey.shade300,
              ),
            );
          });
        },
      ),
    );
  }

  Widget _buildBottomActionBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 10,
            offset: const Offset(0, -3),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Ingin mencocokkan pakaian yang kamu miliki?',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: controller.openGalleryUpload,
                  icon: const Icon(Icons.photo_library_outlined),
                  label: const Text('Galeri'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: controller.openCameraScanner,
                  icon: const Icon(Icons.camera_alt_outlined),
                  label: const Text('Scan Kamera'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
