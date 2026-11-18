import 'package:get/get.dart';
import 'package:mobile/app/routes/app_routes.dart';

/// Controller untuk halaman Beranda ColorFit.
class HomeController extends GetxController {
  void startExploration() {
    Get.toNamed(Routes.UNDERTONE);
  }

  void openHistory() {
    Get.toNamed(Routes.HISTORY);
  }
}
