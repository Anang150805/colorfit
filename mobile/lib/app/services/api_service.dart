import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:mobile/app/core/constants.dart';
import 'package:mobile/app/models/color_result.dart';
import 'package:mobile/app/models/recommendation.dart';

/// Pengecualian khusus untuk kegagalan panggilan API ColorFit.
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

/// Service komunikasi HTTP ke Backend ColorFit.
class ApiService extends GetxService {
  final http.Client _client = http.Client();

  // ---------------------------------------------------------------------------
  // Helper: decode JSON dengan penanganan format tidak valid
  // ---------------------------------------------------------------------------
  Map<String, dynamic> _decodeJson(String body) {
    try {
      return jsonDecode(body) as Map<String, dynamic>;
    } catch (_) {
      throw ApiException('Server merespons dengan format tidak terduga. Coba lagi nanti.');
    }
  }

  // ---------------------------------------------------------------------------
  // Helper: pesan error ramah dari exception
  // ---------------------------------------------------------------------------
  Never _handleNetworkError(Object e, String context) {
    if (e is ApiException) {
      throw e;
    } else if (e is SocketException) {
      throw ApiException(
        'Tidak dapat terhubung ke server ColorFit. '
        'Periksa koneksi internet atau alamat server ($context).',
      );
    } else if (e is TimeoutException) {
      throw ApiException(
        'Koneksi ke server habis waktu ($context). '
        'Coba lagi atau periksa koneksi jaringan Anda.',
      );
    } else {
      throw ApiException('Terjadi kesalahan tidak terduga ($context): $e');
    }
  }

  // ---------------------------------------------------------------------------
  // 1. POST /api/classify
  // ---------------------------------------------------------------------------
  /// Mengambil rekomendasi palet warna berdasarkan undertone (warm, cool, neutral).
  Future<ClassifyResult> classify(String undertone) async {
    if (AppConstants.useDummyData) return _getDummyClassify(undertone);

    final uri = Uri.parse('${AppConstants.baseUrl}${AppConstants.classifyEndpoint}');
    try {
      final response = await _client
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'undertone': undertone}),
          )
          .timeout(AppConstants.classifyTimeout);

      final decoded = _decodeJson(response.body);
      if (response.statusCode == 200 && decoded['success'] == true) {
        return ClassifyResult.fromMap(decoded);
      } else {
        final message = decoded['message']?.toString() ?? 'Gagal memuat palet warna.';
        throw ApiException(message, statusCode: response.statusCode);
      }
    } catch (e) {
      _handleNetworkError(e, '/api/classify');
    }
  }

  // ---------------------------------------------------------------------------
  // 2. POST /api/detect
  // ---------------------------------------------------------------------------
  /// Deteksi cepat warna dominan dari frame kamera kecil (timeout 5 detik).
  Future<String> detect(Uint8List imageBytes) async {
    if (AppConstants.useDummyData) return '#B7410E';

    final uri = Uri.parse('${AppConstants.baseUrl}${AppConstants.detectEndpoint}');
    try {
      final request = http.MultipartRequest('POST', uri);
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: 'frame.jpg',
          contentType: MediaType('image', 'jpeg'),
        ),
      );

      final streamedResponse = await request.send().timeout(AppConstants.detectTimeout);
      final response = await http.Response.fromStream(streamedResponse);

      final decoded = _decodeJson(response.body);
      if (response.statusCode == 200 && decoded['success'] == true) {
        return decoded['hex']?.toString() ?? '#FFFFFF';
      } else {
        final message = decoded['message']?.toString() ?? 'Gagal mendeteksi warna.';
        throw ApiException(message, statusCode: response.statusCode);
      }
    } catch (e) {
      _handleNetworkError(e, '/api/detect');
    }
  }

  // ---------------------------------------------------------------------------
  // 3. POST /api/analyze
  // ---------------------------------------------------------------------------
  /// Analisis mendalam citra pakaian (timeout 30 detik).
  Future<AnalyzeResult> analyze(
    Uint8List imageBytes,
    String undertone, {
    String filename = 'clothing.jpg',
  }) async {
    if (AppConstants.useDummyData) return _getDummyAnalyze(undertone);

    final uri = Uri.parse('${AppConstants.baseUrl}${AppConstants.analyzeEndpoint}');
    try {
      final request = http.MultipartRequest('POST', uri);
      request.fields['undertone'] = undertone;

      final isPng = filename.toLowerCase().endsWith('.png');
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: filename,
          contentType: MediaType('image', isPng ? 'png' : 'jpeg'),
        ),
      );

      final streamedResponse = await request.send().timeout(AppConstants.analyzeTimeout);
      final response = await http.Response.fromStream(streamedResponse);

      final decoded = _decodeJson(response.body);
      if (response.statusCode == 200 && decoded['success'] == true) {
        return AnalyzeResult.fromMap(decoded);
      } else {
        final message = decoded['message']?.toString() ??
            'Analisis pakaian gagal. Silakan ambil ulang foto dengan pencahayaan yang lebih baik.';
        throw ApiException(message, statusCode: response.statusCode);
      }
    } catch (e) {
      _handleNetworkError(e, '/api/analyze');
    }
  }

  // ===========================================================================
  // DUMMY DATA UNTUK MODE PENGEMBANGAN TANPA SERVER BACKEND
  // Aktifkan dengan: AppConstants.useDummyData = true di constants.dart
  // ===========================================================================
  ClassifyResult _getDummyClassify(String undertone) {
    final List<ColorItem> colors = [
      ColorItem(name: 'Merah Bata', hex: '#B7410E', family: 'merah', suitability: 'Sangat Cocok'),
      ColorItem(name: 'Kuning Mustard', hex: '#E1AD01', family: 'kuning', suitability: 'Sangat Cocok'),
      ColorItem(name: 'Hijau Olive', hex: '#556B2F', family: 'hijau', suitability: 'Sangat Cocok'),
      ColorItem(name: 'Oranye Terakota', hex: '#CC4E2A', family: 'oranye', suitability: 'Sangat Cocok'),
      ColorItem(name: 'Coklat Camel', hex: '#C19A6B', family: 'coklat', suitability: 'Sangat Cocok'),
      ColorItem(name: 'Krem Hangat', hex: '#F5F5DC', family: 'netral', suitability: 'Sangat Cocok'),
      ColorItem(name: 'Biru Teal Hangat', hex: '#008080', family: 'biru', suitability: 'Cocok'),
      ColorItem(name: 'Pink Coral', hex: '#F88379', family: 'pink', suitability: 'Cocok'),
      ColorItem(name: 'Ungu Plum Hangat', hex: '#701C3C', family: 'ungu', suitability: 'Cocok'),
      ColorItem(name: 'Biru Elektrik Dingin', hex: '#0000FF', family: 'biru', suitability: 'Kurang Cocok'),
      ColorItem(name: 'Ungu Lavender Icy', hex: '#967BB6', family: 'ungu', suitability: 'Kurang Cocok'),
    ];
    return ClassifyResult(success: true, undertone: undertone, colors: colors);
  }

  AnalyzeResult _getDummyAnalyze(String undertone) {
    return AnalyzeResult(
      success: true,
      detected: DetectedColor(
        hex: '#B7410E',
        rgb: [183, 65, 14],
        hsv: [18.11, 0.92, 0.72],
        lab: [43.91, 46.60, 52.27],
      ),
      suitability: 'Sangat Cocok',
      recommendations: [
        RecommendationItem(
          name: 'Celana Chino Camel',
          hex: '#C19A6B',
          harmony: 'Analogous',
          explanation: 'Kombinasi warna bersebelahan pada roda warna, menciptakan tampilan selaras dan nyaman.',
          distance: 11.45,
          suitability: 'Sangat Cocok',
        ),
        RecommendationItem(
          name: 'Celana Khaki Krem',
          hex: '#D2B48C',
          harmony: 'Monochromatic',
          explanation: 'Kombinasi warna senada dari satu rumpun warna, memberikan kesan rapi dan minimalis.',
          distance: 14.82,
          suitability: 'Sangat Cocok',
        ),
        RecommendationItem(
          name: 'Celana Denim Navy',
          hex: '#000080',
          harmony: 'Complementary',
          explanation: 'Kombinasi warna berseberangan dengan kontras tegas dan memikat.',
          distance: 18.20,
          suitability: 'Cocok',
        ),
        RecommendationItem(
          name: 'Celana Chino Olive',
          hex: '#556B2F',
          harmony: 'Triadic',
          explanation: 'Kombinasi sudut warna yang kaya variasi visual namun tetap seimbang.',
          distance: 22.05,
          suitability: 'Cocok',
        ),
      ],
      message: null,
    );
  }

  @override
  void onClose() {
    _client.close();
    super.onClose();
  }
}
