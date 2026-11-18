import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mobile/app/controllers/home_controller.dart';
import 'package:mobile/app/core/theme.dart';

/// Halaman 1: Beranda ColorFit.
class HomeView extends GetView<HomeController> {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),
              // Icon & Branding Visual
              Center(
                child: Container(
                  width: 110,
                  height: 110,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppTheme.primaryColor, Color(0xFFD74826), AppTheme.accentColor],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primaryColor.withOpacity(0.35),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.palette_outlined,
                    size: 56,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 32),
              // Judul Aplikasi
              Text(
                'ColorFit',
                textAlign: TextAlign.center,
                style: theme.textTheme.headlineLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5,
                  color: AppTheme.primaryColor,
                ),
              ),
              const SizedBox(height: 12),
              // Tagline dan Deskripsi Singkat
              Text(
                'Temukan padu-padan warna pakaian terbaik yang paling selaras dan memesona dengan undertone kulitmu.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.textTheme.bodyMedium?.color?.withOpacity(0.75),
                  height: 1.5,
                ),
              ),
              const Spacer(),
              // Fitur Utama Highlight
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: theme.dividerColor.withOpacity(0.1),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildFeatureItem(Icons.face_retouching_natural, 'Analisis\nUndertone'),
                    _buildDivider(theme),
                    _buildFeatureItem(Icons.center_focus_strong, 'Scan\nPakaian'),
                    _buildDivider(theme),
                    _buildFeatureItem(Icons.style, 'Harmoni\nOutfit'),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              // Tombol Mulai
              ElevatedButton.icon(
                onPressed: controller.startExploration,
                icon: const Icon(Icons.arrow_forward_rounded),
                label: const Text('Mulai Eksplorasi Warna'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              const SizedBox(height: 12),
              // Tombol Riwayat
              OutlinedButton.icon(
                onPressed: controller.openHistory,
                icon: const Icon(Icons.history_rounded),
                label: const Text('Lihat Riwayat Pemindaian'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String label) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 28, color: AppTheme.secondaryColor),
        const SizedBox(height: 6),
        Text(
          label,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  Widget _buildDivider(ThemeData theme) {
    return Container(
      height: 36,
      width: 1,
      color: theme.dividerColor.withOpacity(0.25),
    );
  }
}
