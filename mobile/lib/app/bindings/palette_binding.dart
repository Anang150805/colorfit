import 'package:get/get.dart';
import 'package:mobile/app/controllers/palette_controller.dart';

class PaletteBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<PaletteController>(() => PaletteController());
  }
}
