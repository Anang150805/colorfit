/// Konstanta dan Konfigurasi Aplikasi ColorFit.
class AppConstants {
  /// Base URL untuk backend API ColorFit.
  /// Dikonfigurasi via --dart-define=API_BASE_URL=<url> saat build/run.
  /// - Default: 'http://10.0.2.2:5000' (Android Emulator → localhost PC)
  /// - HP fisik: flutter run --dart-define=API_BASE_URL=http://192.168.x.x:5000
  /// - Produksi: flutter build apk --release --dart-define=API_BASE_URL=https://api.colorfit.app
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:5000',
  );

  // Endpoint Backend API
  static const String classifyEndpoint = '/api/classify';
  static const String detectEndpoint = '/api/detect';
  static const String analyzeEndpoint = '/api/analyze';
  static const String healthEndpoint = '/health';

  /// Timeout untuk POST /api/detect (ringan, hanya K-Means kecil)
  static const Duration detectTimeout = Duration(seconds: 5);

  /// Timeout untuk POST /api/analyze (berat: GrabCut + KNN + DT)
  static const Duration analyzeTimeout = Duration(seconds: 30);

  /// Timeout untuk POST /api/classify
  static const Duration classifyTimeout = Duration(seconds: 15);

  /// Flag simulasi data offline (Dummy Data).
  /// - Jika `true`: ApiService mengembalikan mock dummy data tanpa server backend.
  /// - Jika `false`: ApiService memanggil server Flask backend sungguhan.
  static const bool useDummyData = false;

  // Kunci SharedPreferences
  static const String keyDeviceId = 'colorfit_device_id';
  static const String keySelectedUndertone = 'colorfit_selected_undertone';

  // Opsi Undertone
  static const String undertoneWarm = 'warm';
  static const String undertoneCool = 'cool';
  static const String undertoneNeutral = 'neutral';
}
