"""Benchmark Skrip untuk Mengukur Performa /api/detect dan /api/analyze.

Mengukur waktu rata-rata, minimum, dan maksimum eksekusi endpoint (minimal 20 iterasi).
Menggunakan sampel gambar di tests/sample_images/ atau membangkitkan citra sintetis bila folder kosong.
"""

import os
import sys
import io
import time
import logging
import numpy as np
import cv2

# Tambahkan direktori root backend ke sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("colorfit.benchmark")

NUM_ITERATIONS = 20
SAMPLE_DIR = os.path.join(BACKEND_DIR, "tests", "sample_images")


def get_benchmark_image_bytes() -> bytes:
    """Mengambil byte gambar dari tests/sample_images/ atau membangkitkan citra sintetis."""
    valid_exts = (".jpg", ".jpeg", ".png")
    if os.path.exists(SAMPLE_DIR):
        files = [f for f in os.listdir(SAMPLE_DIR) if f.lower().endswith(valid_exts)]
        if files:
            sample_path = os.path.join(SAMPLE_DIR, files[0])
            logger.info(f"Menggunakan sampel gambar asli dari: {sample_path}")
            with open(sample_path, "rb") as f:
                return f.read()

    logger.info("Folder tests/sample_images/ tidak berisi foto. Membangkitkan citra pakaian sintetis...")
    # Buat citra sintetis 300x300 dengan latar netral dan pakaian merah bata di tengah
    img = np.full((300, 300, 3), 210, dtype=np.uint8)
    # Bounding box pakaian merah bata BGR (14, 65, 183)
    img[50:250, 50:250] = (14, 65, 183)
    _, encoded = cv2.imencode(".png", img)
    return encoded.tobytes()


def run_benchmark():
    logger.info(f"=== MEMULAI BENCHMARK PERFORMA BACKEND COLORFIT ({NUM_ITERATIONS} ITERASI) ===")
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    image_bytes = get_benchmark_image_bytes()

    # 1. Benchmark /api/detect (Mode Cepat Kamera)
    logger.info(f"Menjalankan benchmark POST /api/detect ({NUM_ITERATIONS} kali)...")
    detect_times = []

    for i in range(NUM_ITERATIONS):
        data = {
            "image": (io.BytesIO(image_bytes), "detect_frame.jpg")
        }
        start = time.perf_counter()
        resp = client.post("/api/detect", data=data, content_type="multipart/form-data")
        elapsed = (time.perf_counter() - start) * 1000.0  # ms
        assert resp.status_code == 200, f"Error pada iterasi {i}: {resp.data}"
        detect_times.append(elapsed)

    # 2. Benchmark /api/analyze (Mode Lengkap GrabCut + KNN + DT)
    logger.info(f"Menjalankan benchmark POST /api/analyze ({NUM_ITERATIONS} kali)...")
    analyze_times = []

    for i in range(NUM_ITERATIONS):
        data = {
            "image": (io.BytesIO(image_bytes), "clothing_photo.jpg"),
            "undertone": "warm"
        }
        start = time.perf_counter()
        resp = client.post("/api/analyze", data=data, content_type="multipart/form-data")
        elapsed = (time.perf_counter() - start) * 1000.0  # ms
        assert resp.status_code == 200, f"Error pada iterasi {i}: {resp.data}"
        analyze_times.append(elapsed)

    # Ringkasan Hasil
    print("\n" + "=" * 65)
    print("HASIL BENCHMARK LATENSI API COLORFIT (Satuan: milidetik / ms)")
    print("=" * 65)
    print(f"{'Endpoint':<20} | {'Rata-rata':>10} | {'Min':>8} | {'Maks':>8} | {'Std Dev':>8}")
    print("-" * 65)
    print(
        f"{'POST /api/detect':<20} | {np.mean(detect_times):>9.2f}ms | {np.min(detect_times):>7.2f}ms | "
        f"{np.max(detect_times):>7.2f}ms | {np.std(detect_times):>7.2f}ms"
    )
    print(
        f"{'POST /api/analyze':<20} | {np.mean(analyze_times):>9.2f}ms | {np.min(analyze_times):>7.2f}ms | "
        f"{np.max(analyze_times):>7.2f}ms | {np.std(analyze_times):>7.2f}ms"
    )
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_benchmark()
