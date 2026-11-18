import 'package:flutter/material.dart';
import 'package:mobile/app/core/utils.dart';
import 'package:mobile/app/models/recommendation.dart';
import 'package:mobile/app/widgets/color_chip.dart';

/// Kartu untuk menampilkan item paduan pakaian hasil rekomendasi KNN dan Color Harmony Itten.
class HarmonyCard extends StatelessWidget {
  final RecommendationItem recommendation;

  const HarmonyCard({
    super.key,
    required this.recommendation,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final comboColor = AppUtils.hexToColor(recommendation.hex);

    return Card(
      elevation: 1.5,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: theme.dividerColor.withOpacity(0.1),
        ),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Baris Atas: Swatch Warna, Nama Outfit, dan Jarak
            Row(
              children: [
                ColorChipWidget(
                  hex: recommendation.hex,
                  size: 42,
                  showHexText: false,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        recommendation.name,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        recommendation.hex.toUpperCase(),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                          fontFamily: 'monospace',
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                // Badge Jarak CIELAB
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'ΔE: ${recommendation.distance.toStringAsFixed(1)}',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 20),
            // Tag Tipe Harmoni
            Row(
              children: [
                Icon(
                  Icons.auto_awesome,
                  size: 16,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  recommendation.harmony,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            // Kalimat Penjelasan Bahasa Indonesia
            Text(
              recommendation.explanation,
              style: TextStyle(
                fontSize: 13,
                height: 1.4,
                color: theme.textTheme.bodyMedium?.color?.withOpacity(0.85),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
