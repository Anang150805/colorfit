import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:mobile/app/models/color_result.dart';
import 'package:mobile/app/models/recommendation.dart';

/// Model dokumen riwayat pemindaian ColorFit yang disimpan di Firestore.
/// Jalur koleksi: devices/{device_id}/histories/{id}
class HistoryItem {
  final String id;
  final String undertone;
  final DetectedColor detected;
  final String suitability;
  final List<RecommendationItem> recommendations;
  final DateTime createdAt;

  HistoryItem({
    required this.id,
    required this.undertone,
    required this.detected,
    required this.suitability,
    required this.recommendations,
    required this.createdAt,
  });

  factory HistoryItem.fromMap(Map<String, dynamic> map, String docId) {
    DateTime parsedDate = DateTime.now();
    if (map['createdAt'] is Timestamp) {
      parsedDate = (map['createdAt'] as Timestamp).toDate();
    } else if (map['createdAt'] is String) {
      parsedDate = DateTime.tryParse(map['createdAt']) ?? DateTime.now();
    } else if (map['createdAt'] is int) {
      parsedDate = DateTime.fromMillisecondsSinceEpoch(map['createdAt']);
    }

    DetectedColor detectedColor;
    if (map['detected'] is Map<String, dynamic>) {
      detectedColor = DetectedColor.fromMap(map['detected'] as Map<String, dynamic>);
    } else {
      detectedColor = DetectedColor(
        hex: '#FFFFFF',
        rgb: [255, 255, 255],
        hsv: [0, 0, 1],
        lab: [100, 0, 0],
      );
    }

    final rawRecs = map['recommendations'] as List<dynamic>? ?? [];
    final recommendations = rawRecs
        .whereType<Map<String, dynamic>>()
        .map((r) => RecommendationItem.fromMap(r))
        .toList();

    return HistoryItem(
      id: docId,
      undertone: map['undertone']?.toString() ?? 'warm',
      detected: detectedColor,
      suitability: map['suitability']?.toString() ?? 'Cocok',
      recommendations: recommendations,
      createdAt: parsedDate,
    );
  }

  Map<String, dynamic> toMap({bool useServerTimestamp = true}) {
    return {
      'undertone': undertone,
      'detected': detected.toMap(),
      'suitability': suitability,
      'recommendations': recommendations.map((r) => r.toMap()).toList(),
      'createdAt': useServerTimestamp ? FieldValue.serverTimestamp() : createdAt.toIso8601String(),
    };
  }
}
