import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';
import 'package:mobile/app/core/utils.dart';

/// Widget chip warna yang menampilkan swatch warna, nama, dan kode HEX.
/// Mengetuk chip akan menyalin kode HEX ke papan klip (clipboard).
class ColorChipWidget extends StatelessWidget {
  final String hex;
  final String? name;
  final double size;
  final bool showHexText;

  const ColorChipWidget({
    super.key,
    required this.hex,
    this.name,
    this.size = 36.0,
    this.showHexText = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = AppUtils.hexToColor(hex);

    return InkWell(
      onTap: () {
        Clipboard.setData(ClipboardData(text: hex));
        Get.snackbar(
          'Warna Disalin',
          'Kode $hex telah disalin ke papan klip.',
          snackPosition: SnackPosition.BOTTOM,
          duration: const Duration(seconds: 2),
          margin: const EdgeInsets.all(12),
          backgroundColor: Colors.black87,
          colorText: Colors.white,
          icon: const Icon(Icons.copy, color: Colors.white, size: 20),
        );
      },
      borderRadius: BorderRadius.circular(10),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
                border: Border.all(
                  color: Colors.black12,
                  width: 1.5,
                ),
                boxShadow: [
                  BoxShadow(
                    color: color.withOpacity(0.3),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
            ),
            if (showHexText || name != null) ...[
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (name != null)
                    Text(
                      name!,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  if (showHexText)
                    Text(
                      hex.toUpperCase(),
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey.shade600,
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
