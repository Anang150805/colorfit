import 'package:flutter/material.dart';
import 'package:mobile/app/core/utils.dart';

/// Badge visual untuk menampilkan status kesesuaian warna ('Sangat Cocok', 'Cocok', 'Kurang Cocok').
class SuitabilityBadge extends StatelessWidget {
  final String suitability;
  final bool isLarge;

  const SuitabilityBadge({
    super.key,
    required this.suitability,
    this.isLarge = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = AppUtils.getSuitabilityColor(suitability);
    final icon = AppUtils.getSuitabilityIcon(suitability);

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isLarge ? 14 : 10,
        vertical: isLarge ? 7 : 4,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: color.withOpacity(0.5),
          width: 1.2,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: isLarge ? 18 : 14,
            color: color,
          ),
          const SizedBox(width: 5),
          Text(
            suitability,
            style: TextStyle(
              color: color,
              fontSize: isLarge ? 13 : 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.2,
            ),
          ),
        ],
      ),
    );
  }
}
