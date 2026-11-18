import 'package:mobile/app/models/recommendation.dart';

/// Item warna hasil klasifikasi palet undertone (/api/classify).
class ColorItem {
  final String name;
  final String hex;
  final String family;
  final String suitability;

  ColorItem({
    required this.name,
    required this.hex,
    required this.family,
    required this.suitability,
  });

  factory ColorItem.fromMap(Map<String, dynamic> map) {
    return ColorItem(
      name: map['name']?.toString() ?? '',
      hex: map['hex']?.toString() ?? '#FFFFFF',
      family: map['family']?.toString() ?? 'netral',
      suitability: map['suitability']?.toString() ?? 'Cocok',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'hex': hex,
      'family': family,
      'suitability': suitability,
    };
  }
}

/// Respons dari POST /api/classify.
class ClassifyResult {
  final bool success;
  final String undertone;
  final List<ColorItem> colors;
  final String? message;

  ClassifyResult({
    required this.success,
    required this.undertone,
    required this.colors,
    this.message,
  });

  factory ClassifyResult.fromMap(Map<String, dynamic> map) {
    final rawColors = map['colors'] as List<dynamic>? ?? [];
    return ClassifyResult(
      success: map['success'] == true,
      undertone: map['undertone']?.toString() ?? '',
      colors: rawColors
          .whereType<Map<String, dynamic>>()
          .map((c) => ColorItem.fromMap(c))
          .toList(),
      message: map['message']?.toString(),
    );
  }
}

/// Representasi ruang warna lengkap dari warna yang terdeteksi.
class DetectedColor {
  final String hex;
  final List<int> rgb;
  final List<double> hsv;
  final List<double> lab;

  DetectedColor({
    required this.hex,
    required this.rgb,
    required this.hsv,
    required this.lab,
  });

  factory DetectedColor.fromMap(Map<String, dynamic> map) {
    final rawRgb = (map['rgb'] as List<dynamic>? ?? [0, 0, 0])
        .map((e) => (e is num) ? e.toInt() : int.tryParse(e.toString()) ?? 0)
        .toList();

    final rawHsv = (map['hsv'] as List<dynamic>? ?? [0.0, 0.0, 0.0])
        .map((e) => (e is num) ? e.toDouble() : double.tryParse(e.toString()) ?? 0.0)
        .toList();

    final rawLab = (map['lab'] as List<dynamic>? ?? [0.0, 0.0, 0.0])
        .map((e) => (e is num) ? e.toDouble() : double.tryParse(e.toString()) ?? 0.0)
        .toList();

    return DetectedColor(
      hex: map['hex']?.toString() ?? '#FFFFFF',
      rgb: rawRgb,
      hsv: rawHsv,
      lab: rawLab,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'hex': hex,
      'rgb': rgb,
      'hsv': hsv,
      'lab': lab,
    };
  }
}

/// Respons dari POST /api/analyze.
class AnalyzeResult {
  final bool success;
  final DetectedColor? detected;
  final String suitability;
  final List<RecommendationItem> recommendations;
  final String? message;

  AnalyzeResult({
    required this.success,
    this.detected,
    required this.suitability,
    required this.recommendations,
    this.message,
  });

  factory AnalyzeResult.fromMap(Map<String, dynamic> map) {
    final success = map['success'] == true;
    DetectedColor? detected;
    if (map['detected'] is Map<String, dynamic>) {
      detected = DetectedColor.fromMap(map['detected'] as Map<String, dynamic>);
    }

    final rawRecs = map['recommendations'] as List<dynamic>? ?? [];
    final recommendations = rawRecs
        .whereType<Map<String, dynamic>>()
        .map((r) => RecommendationItem.fromMap(r))
        .toList();

    return AnalyzeResult(
      success: success,
      detected: detected,
      suitability: map['suitability']?.toString() ?? 'Cocok',
      recommendations: recommendations,
      message: map['message']?.toString(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'success': success,
      'detected': detected?.toMap(),
      'suitability': suitability,
      'recommendations': recommendations.map((r) => r.toMap()).toList(),
      'message': message,
    };
  }
}
