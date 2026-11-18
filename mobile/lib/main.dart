import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:mobile/app/core/theme.dart';
import 'package:mobile/app/routes/app_pages.dart';
import 'package:mobile/app/services/api_service.dart';
import 'package:mobile/app/services/device_id_service.dart';
import 'package:mobile/app/services/firestore_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Inisialisasi Firebase Cloud
  // Catatan: Dibungkus dengan blok try-catch agar aplikasi tetap dapat dijalankan
  // meskipun berkas konfigurasi 'google-services.json' belum dipasang oleh pengembang.
  bool isFirebaseInitialized = false;
  try {
    // TODO: Jalankan `flutterfire configure` atau letakkan file `google-services.json`
    // di dalam folder `mobile/android/app/` untuk mengaktifkan sinkronisasi cloud Firestore sepenuhnya.
    await Firebase.initializeApp();
    isFirebaseInitialized = true;
    debugPrint("[Firebase] Inisialisasi Firebase berhasil.");
  } catch (e) {
    debugPrint(
      "[Firebase] Firebase belum dikonfigurasi ($e). "
      "Aplikasi akan tetap berjalan dalam mode penyimpanan riwayat lokal.",
    );
  }

  // Inisialisasi SharedPreferences dan Dependency Injection Global GetX
  final prefs = await SharedPreferences.getInstance();
  Get.put<SharedPreferences>(prefs, permanent: true);
  Get.put<DeviceIdService>(DeviceIdService(prefs), permanent: true);
  Get.put<ApiService>(ApiService(), permanent: true);
  Get.put<FirestoreService>(FirestoreService(isFirebaseInitialized), permanent: true);

  runApp(const ColorFitApp());
}

/// Root Widget Aplikasi ColorFit berbasis GetMaterialApp.
class ColorFitApp extends StatelessWidget {
  const ColorFitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'ColorFit',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      initialRoute: AppPages.INITIAL,
      getPages: AppPages.routes,
      defaultTransition: Transition.cupertino,
    );
  }
}

/// Alias kompatibilitas pengujian bawaan
typedef MyApp = ColorFitApp;
