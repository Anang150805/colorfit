import 'package:get/get.dart';
import 'package:mobile/app/core/constants.dart';
import 'package:mobile/app/models/color_result.dart';
import 'package:mobile/app/models/history_item.dart';
import 'package:mobile/app/routes/app_routes.dart';
import 'package:mobile/app/services/firestore_service.dart';

/// Controller untuk Halaman Hasil Rekomendasi Pakaian (/api/analyze).
class ResultController extends GetxController {
  final FirestoreService _firestoreService = Get.find<FirestoreService>();

  final Rx<AnalyzeResult?> result = Rx<AnalyzeResult?>(null);
  final RxString undertone = AppConstants.undertoneWarm.obs;
  final RxBool isSaved = false.obs;

  @override
  void onInit() {
    super.onInit();
    final args = Get.arguments as Map<String, dynamic>?;
    if (args != null) {
      if (args['analyzeResult'] is AnalyzeResult) {
        result.value = args['analyzeResult'] as AnalyzeResult;
      }
      if (args.containsKey('undertone')) {
        undertone.value = args['undertone'].toString();
      }
    }

    _autoSaveToHistory();
  }

  /// Otomatis menyimpan hasil analisis pakaian ke Firestore
  Future<void> _autoSaveToHistory() async {
    final current = result.value;
    if (current == null || !current.success || current.detected == null) {
      return;
    }

    final historyItem = HistoryItem(
      id: '',
      undertone: undertone.value,
      detected: current.detected!,
      suitability: current.suitability,
      recommendations: current.recommendations,
      createdAt: DateTime.now(),
    );

    await _firestoreService.saveHistory(historyItem);
    isSaved.value = true;
  }

  void retakePhoto() {
    Get.back();
  }

  void backToHome() {
    Get.offAllNamed(Routes.HOME);
  }

  void openHistory() {
    Get.toNamed(Routes.HISTORY);
  }
}
