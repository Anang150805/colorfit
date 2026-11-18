/// Model untuk item rekomendasi padu-padan pakaian dari KNN & Color Harmony.
class RecommendationItem {
  final String name;
  final String hex;
  final String harmony;
  final String explanation;
  final double distance;
  /// Penilaian kesesuaian: 'Sangat Cocok' | 'Cocok' | 'Kurang Cocok'
  final String suitability;

  RecommendationItem({
    required this.name,
    required this.hex,
    required this.harmony,
    required this.explanation,
    required this.distance,
    this.suitability = 'Cocok',
  });

  factory RecommendationItem.fromMap(Map<String, dynamic> map) {
    return RecommendationItem(
      name: map['name']?.toString() ?? '',
      hex: map['hex']?.toString() ?? '#FFFFFF',
      harmony: map['harmony']?.toString() ?? 'Netral',
      explanation: map['explanation']?.toString() ?? '',
      distance: (map['distance'] is num)
          ? (map['distance'] as num).toDouble()
          : double.tryParse(map['distance']?.toString() ?? '0.0') ?? 0.0,
      suitability: map['suitability']?.toString() ?? 'Cocok',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'hex': hex,
      'harmony': harmony,
      'explanation': explanation,
      'distance': distance,
      'suitability': suitability,
    };
  }
}
