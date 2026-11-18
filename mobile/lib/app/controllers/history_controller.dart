import 'package:get/get.dart';
import 'package:mobile/app/models/color_result.dart';
import 'package:mobile/app/models/history_item.dart';
import 'package:mobile/app/routes/app_routes.dart';
import 'package:mobile/app/services/firestore_service.dart';

/// Controller untuk Halaman Riwayat Pemindaian Pakaian (Firestore History).
class HistoryController extends GetxController {
  final FirestoreService _firestoreService = Get.find<FirestoreService>();

  final RxList<HistoryItem> histories = <HistoryItem>[].obs;
  final RxBool isLoading = true.obs;

  bool get isFirebaseAvailable => _firestoreService.isFirebaseAvailable;

  @override
  void onInit() {
    super.onInit();
    bindHistories();
  }

  void bindHistories() {
    isLoading.value = true;
    _firestoreService.streamHistories().listen(
      (list) {
        histories.assignAll(list);
        isLoading.value = false;
      },
      onError: (err) {
        isLoading.value = false;
      },
    );
  }

  Future<void> refreshHistories() async {
    isLoading.value = true;
    final list = await _firestoreService.fetchHistories();
    histories.assignAll(list);
    isLoading.value = false;
  }

  /// Membuka kembali detail riwayat pada Halaman Hasil (ResultView)
  void openDetail(HistoryItem item) {
    final analyzeResult = AnalyzeResult(
      success: true,
      detected: item.detected,
      suitability: item.suitability,
      recommendations: item.recommendations,
      message: null,
    );

    Get.toNamed(
      Routes.RESULT,
      arguments: {
        'analyzeResult': analyzeResult,
        'undertone': item.undertone,
      },
    );
  }
}
