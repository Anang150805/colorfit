import 'package:get/get.dart';
import 'package:mobile/app/controllers/undertone_controller.dart';

class UndertoneBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<UndertoneController>(() => UndertoneController());
  }
}
