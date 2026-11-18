# ColorFit Mobile — Panduan Pengembang

Aplikasi Flutter untuk rekomendasi padu-padan pakaian berdasarkan undertone kulit. Terdiri dari 7 halaman: Beranda, Pilih Undertone, Rekomendasi Palet, Scan Kamera, Unggah Foto, Hasil Analisis, dan Riwayat.

---

## Prasyarat

| Alat | Versi Minimum |
|------|--------------|
| Flutter SDK | 3.10.7 |
| Dart SDK | 3.10.7 (bundled dengan Flutter) |
| Android Studio / VS Code | Terbaru |
| Android SDK / Emulator | API 21+ |
| Node.js (opsional) | Untuk Firebase CLI |
| Firebase CLI (opsional) | `npm install -g firebase-tools` |

---

## Clone & Install Dependensi

```bash
git clone <repo-url>
cd colorfit/mobile
flutter pub get
```

---

## Konfigurasi Firebase (Opsional — hanya untuk Riwayat Cloud)

> [!NOTE]
> Aplikasi tetap berjalan **tanpa Firebase**. Tanpa konfigurasi ini, riwayat hanya tersimpan di memori (hilang saat app ditutup), dan Firestore tidak aktif.

1. Buat project di [Firebase Console](https://console.firebase.google.com/).
2. Aktifkan **Cloud Firestore** (mode uji/test mode).
3. Install FlutterFire CLI:
   ```bash
   dart pub global activate flutterfire_cli
   ```
4. Jalankan konfigurasi (dari folder `mobile/`):
   ```bash
   flutterfire configure
   ```
   Ini akan menghasilkan `lib/firebase_options.dart` dan `android/app/google-services.json`.

> [!CAUTION]
> **Keamanan Firestore**: Aturan Firestore mode uji **kedaluwarsa ±30 hari** setelah dibuat. Tanpa autentikasi, siapa pun yang mengetahui `device_id` pengguna dapat membaca riwayat mereka. **Hanya gunakan untuk demo/pengembangan, bukan produksi.**

---

## Menjalankan di Emulator Android

Backend Flask harus berjalan di PC (port 5000). Emulator Android mengakses localhost PC melalui IP khusus `10.0.2.2`:

```bash
# Jalankan backend terlebih dahulu (dari folder colorfit/backend/)
python app.py

# Lalu jalankan Flutter di emulator
cd colorfit/mobile
flutter run
```

Nilai default `baseUrl` sudah `http://10.0.2.2:5000`, tidak perlu parameter tambahan.

---

## Menjalankan di HP Fisik (USB Debugging / WiFi)

Ganti alamat IP dengan IP lokal laptop Anda (cek dengan `ipconfig` di Windows atau `ifconfig` di Mac/Linux):

```bash
flutter run --dart-define=API_BASE_URL=http://192.168.1.10:5000
```

Pastikan HP dan laptop berada di jaringan WiFi yang sama, dan firewall PC mengizinkan koneksi masuk ke port 5000.

---

## Build APK Release (Produksi)

```bash
flutter build apk --release --dart-define=API_BASE_URL=https://api.colorfit.app
```

APK dihasilkan di `build/app/outputs/flutter-apk/app-release.apk`.

---

## Mode Dummy (Tanpa Backend)

Untuk menguji UI tanpa server Flask:

1. Buka `lib/app/core/constants.dart`
2. Ubah: `static const bool useDummyData = false;` → `true`
3. Jalankan `flutter run` seperti biasa

Semua API call akan mengembalikan data contoh hard-coded tanpa menyentuh jaringan.

---

## Struktur Proyek

```
mobile/lib/
├── main.dart                        # Entry point, inisialisasi Firebase & GetX
├── app/
│   ├── core/
│   │   ├── constants.dart           # baseUrl, timeouts, kunci SharedPreferences
│   │   ├── theme.dart               # Material 3, warna branding ColorFit
│   │   └── utils.dart               # hexToColor, getSuitabilityColor, dll.
│   ├── models/
│   │   ├── color_result.dart        # ColorItem, ClassifyResult, DetectedColor, AnalyzeResult
│   │   ├── recommendation.dart      # RecommendationItem (name, hex, harmony, suitability)
│   │   └── history_item.dart        # HistoryItem (Firestore toMap/fromMap)
│   ├── services/
│   │   ├── api_service.dart         # HTTP client: classify, detect, analyze
│   │   ├── firestore_service.dart   # Firestore: histories + device undertone
│   │   └── device_id_service.dart   # UUID v4 persisten di SharedPreferences
│   ├── controllers/                 # GetX controllers (7 halaman)
│   ├── views/                       # Widget halaman (7 halaman)
│   ├── bindings/                    # GetX bindings (7 halaman)
│   ├── widgets/
│   │   ├── color_chip.dart          # Swatch warna + salin HEX
│   │   ├── suitability_badge.dart   # Badge Sangat Cocok / Cocok / Kurang Cocok
│   │   └── harmony_card.dart        # Kartu rekomendasi padu-padan
│   └── routes/
│       ├── app_routes.dart          # Nama-nama route konstanta
│       └── app_pages.dart           # GetPages dengan binding
└── assets/
    └── images/                      # Aset gambar (isi sendiri)
```

---

## Kontrak API Backend

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/classify` | POST | Rekomendasi palet berdasarkan undertone |
| `/api/detect` | POST (multipart) | Deteksi cepat warna dominan frame kamera |
| `/api/analyze` | POST (multipart) | Analisis mendalam + rekomendasi padu-padan |
| `/health` | GET | Cek status server |

Lihat `backend/README.md` untuk detail lengkap dan contoh `curl`.

---

## Catatan Teknis Kamera

- **Stream**: Menggunakan `startImageStream` dengan `ResolutionPreset.low` agar tidak ada suara rana atau kedip layar.
- **Throttle**: Satu frame per detik dikirim ke `/api/detect`; frame dilewati jika permintaan sebelumnya belum selesai.
- **Konversi YUV**: Frame YUV420 dikonversi ke JPEG (lebar maks 160 px) di isolate `compute()` agar UI tidak tersendat.
- **Background**: Stream dihentikan otomatis saat app masuk background (`WidgetsBindingObserver`).

---

## Lisensi

Proyek ini dibuat untuk keperluan akademik (Proposal Mobile ColorFit — Kelompok 5).
