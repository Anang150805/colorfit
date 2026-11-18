import 'package:flutter/material.dart';
import 'package:mobile/app/core/theme.dart';

/// Utilitas pendukung aplikasi ColorFit.
class AppUtils {
  /// Mengonversi string HEX (misal: '#B7410E' atau 'B7410E') menjadi Color Flutter.
  static Color hexToColor(String hexStr) {
    try {
      final clean = hexStr.replaceAll('#', '').trim();
      if (clean.length == 6) {
        return Color(int.parse('FF$clean', radix: 16));
      } else if (clean.length == 8) {
        return Color(int.parse(clean, radix: 16));
      }
    } catch (_) {
      // Fallback warna abu-abu bila parsing gagal
    }
    return const Color(0xFF9E9E9E);
  }

  /// Mengonversi objek Color Flutter menjadi string HEX (misal: '#RRGGBB').
  static String colorToHex(Color color) {
    final r = color.red.toRadixString(16).padLeft(2, '0').toUpperCase();
    final g = color.green.toRadixString(16).padLeft(2, '0').toUpperCase();
    final b = color.blue.toRadixString(16).padLeft(2, '0').toUpperCase();
    return '#$r$g$b';
  }

  /// Memformat DateTime menjadi string tanggal dan waktu Indonesia yang mudah dibaca.
  static String formatDateTime(DateTime dateTime) {
    final months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
      'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'
    ];
    final day = dateTime.day.toString().padLeft(2, '0');
    final month = months[dateTime.month - 1];
    final year = dateTime.year;
    final hour = dateTime.hour.toString().padLeft(2, '0');
    final minute = dateTime.minute.toString().padLeft(2, '0');

    return '$day $month $year, $hour:$minute WIB';
  }

  /// Menentukan warna indikator berdasarkan teks label kesesuaian.
  static Color getSuitabilityColor(String suitability) {
    final lower = suitability.toLowerCase().trim();
    if (lower.contains('sangat')) {
      return AppTheme.suitableColor;
    } else if (lower.contains('kurang')) {
      return AppTheme.unsuitableColor;
    } else {
      return AppTheme.neutralMatchColor;
    }
  }

  /// Menentukan IconData untuk label kesesuaian.
  static IconData getSuitabilityIcon(String suitability) {
    final lower = suitability.toLowerCase().trim();
    if (lower.contains('sangat')) {
      return Icons.verified;
    } else if (lower.contains('kurang')) {
      return Icons.warning_amber_rounded;
    } else {
      return Icons.check_circle_outline;
    }
  }

  /// Menghitung apakah teks di atas background warna tertentu sebaiknya berwarna putih atau hitam.
  static Color getContrastTextColor(Color backgroundColor) {
    // Luminance CIE standard
    final luminance = backgroundColor.computeLuminance();
    return luminance > 0.5 ? Colors.black87 : Colors.white;
  }
}
