import 'package:get/get.dart';
import 'package:mobile/app/bindings/camera_binding.dart';
import 'package:mobile/app/bindings/history_binding.dart';
import 'package:mobile/app/bindings/home_binding.dart';
import 'package:mobile/app/bindings/palette_binding.dart';
import 'package:mobile/app/bindings/result_binding.dart';
import 'package:mobile/app/bindings/undertone_binding.dart';
import 'package:mobile/app/bindings/upload_binding.dart';
import 'package:mobile/app/routes/app_routes.dart';
import 'package:mobile/app/views/camera_view.dart';
import 'package:mobile/app/views/history_view.dart';
import 'package:mobile/app/views/home_view.dart';
import 'package:mobile/app/views/palette_view.dart';
import 'package:mobile/app/views/result_view.dart';
import 'package:mobile/app/views/undertone_view.dart';
import 'package:mobile/app/views/upload_view.dart';

/// Pendaftaran seluruh GetPages dan Bindings di aplikasi ColorFit.
class AppPages {
  static const INITIAL = Routes.HOME;

  static final routes = [
    GetPage(
      name: Routes.HOME,
      page: () => const HomeView(),
      binding: HomeBinding(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: Routes.UNDERTONE,
      page: () => const UndertoneView(),
      binding: UndertoneBinding(),
      transition: Transition.rightToLeft,
    ),
    GetPage(
      name: Routes.PALETTE,
      page: () => const PaletteView(),
      binding: PaletteBinding(),
      transition: Transition.rightToLeft,
    ),
    GetPage(
      name: Routes.CAMERA,
      page: () => const CameraView(),
      binding: CameraBinding(),
      transition: Transition.downToUp,
    ),
    GetPage(
      name: Routes.UPLOAD,
      page: () => const UploadView(),
      binding: UploadBinding(),
      transition: Transition.rightToLeft,
    ),
    GetPage(
      name: Routes.RESULT,
      page: () => const ResultView(),
      binding: ResultBinding(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: Routes.HISTORY,
      page: () => const HistoryView(),
      binding: HistoryBinding(),
      transition: Transition.rightToLeft,
    ),
  ];
}
