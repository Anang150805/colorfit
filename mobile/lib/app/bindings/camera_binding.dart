import 'package:get/get.dart';
import 'package:mobile/app/controllers/camera_controller.dart';

class CameraBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<CameraScanController>(() => CameraScanController());
  }
}
