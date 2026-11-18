"""Image Processing Service ColorFit.

Revisi K-Means & Pemrosesan Citra:
1. Validasi gambar: format/MIME, integritas piksel cv2.imdecode, batas ukuran 5 MB, batas dimensi maks (4096 px).
2. Klasterisasi K-Means dilakukan dalam ruang warna CIELAB (D65).
3. Mengabaikan piksel yang hampir putih/hitam (background polos atau sorot cahaya).
4. Jika seluruh piksel terbuang, menghasilkan InvalidImageError agar API merespons success: false.
5. Mode /api/detect: crop tengah, resize kecil (96 px), K-Means CIELAB langsung tanpa GrabCut (sangat cepat).
6. Mode /api/analyze: resize (sisi terpanjang maks 640 px), Gaussian Blur, GrabCut dengan rect di tengah,
   fallback ke crop tengah bila foreground < 5%, K-Means CIELAB pada foreground valid.
7. Menggunakan modul logging standar Python, bukan print.
"""

import logging
from typing import Tuple
import numpy as np
import cv2

from services.color_features import lab_to_rgb, rgb_to_hex, rgb_to_hsv

logger = logging.getLogger("colorfit.image_processing")

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_ALLOWED_DIMENSION = 4096  # Batas maksimum dimensi panjang/lebar


class InvalidImageError(Exception):
    """Pengecualian ketika gambar tidak valid, rusak, atau objek pakaian gagal diekstrak."""
    pass


def validate_and_decode_image(image_bytes: bytes) -> np.ndarray:
    """Membaca dan memvalidasi byte gambar mentah menjadi numpy ndarray BGR (OpenCV).
    
    Raises:
        InvalidImageError: Jika gambar kosong, melebihi 5MB, format rusak, atau dimensi tidak wajar.
    """
    if not image_bytes or len(image_bytes) == 0:
        raise InvalidImageError("File gambar kosong atau tidak terbaca.")

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise InvalidImageError("Ukuran file gambar melebihi batas maksimum 5 MB.")

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None or img.size == 0:
        raise InvalidImageError("Format file bukan gambar yang didukung (gunakan JPG atau PNG).")

    h, w = img.shape[:2]
    if h < 20 or w < 20:
        raise InvalidImageError("Dimensi gambar terlalu kecil (minimal 20x20 piksel).")

    if h > MAX_ALLOWED_DIMENSION or w > MAX_ALLOWED_DIMENSION:
        raise InvalidImageError(f"Dimensi gambar ({w}x{h}) melebihi batas maksimal {MAX_ALLOWED_DIMENSION} piksel.")

    # Validasi kecerahan & variasi visual global
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))

    if mean_val < 8.0 and std_val < 6.0:
        raise InvalidImageError(
            "Gambar terlalu gelap atau kurang pencahayaan. Silakan ambil ulang foto di tempat yang lebih terang."
        )

    if mean_val > 250.0 and std_val < 6.0:
        raise InvalidImageError(
            "Gambar terlalu terang atau silau. Silakan ambil ulang foto dengan pencahayaan seimbang."
        )

    if std_val < 1.5:
        raise InvalidImageError(
            "Gambar tidak memiliki variasi objek pakaian (terlalu datar atau polos)."
        )

    return img


def _resize_longest_side(img: np.ndarray, max_dim: int) -> np.ndarray:
    """Mengubah ukuran gambar secara proporsional agar sisi terpanjang <= max_dim."""
    h, w = img.shape[:2]
    longest = max(h, w)
    if longest <= max_dim:
        return img
    scale = max_dim / float(longest)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _bgr_to_cielab_float(bgr_img: np.ndarray) -> np.ndarray:
    """Mengonversi citra BGR uint8 ke CIELAB float32 dengan rentang L*[0, 100], a*[-128, 127], b*[-128, 127]."""
    bgr_f32 = bgr_img.astype(np.float32) / 255.0
    return cv2.cvtColor(bgr_f32, cv2.COLOR_BGR2Lab)


def _filter_extreme_pixels(lab_pixels: np.ndarray) -> np.ndarray:
    """Membuang piksel yang hampir putih pekat atau hitam pekat (latar belakang/sorot cahaya).
    
    Aturan:
    - L* < 8.0: Terlalu gelap (mendekati hitam pekat).
    - L* > 92.0 dan kroma < 14.0: Terlalu terang/silau tanpa saturasi (putih latar).
    - L* > 96.0: Sorotan cahaya ekstrem (highlight).
    """
    if len(lab_pixels) == 0:
        return lab_pixels

    L = lab_pixels[:, 0]
    a = lab_pixels[:, 1]
    b = lab_pixels[:, 2]
    chroma = np.sqrt(a ** 2 + b ** 2)

    # Kondisi piksel valid
    is_not_too_dark = L >= 8.0
    is_not_pure_white = ~((L > 92.0) & (chroma < 14.0))
    is_not_glare = L <= 96.5

    valid_mask = is_not_too_dark & is_not_pure_white & is_not_glare
    return lab_pixels[valid_mask]


def _kmeans_dominant_lab(lab_pixels: np.ndarray, k: int = 3) -> Tuple[float, float, float]:
    """Menjalankan K-Means clustering pada kumpulan piksel CIELAB dan mengembalikan pusat klaster dominan.
    
    Raises:
        InvalidImageError: Jika semua piksel terbuang atau klasterisasi gagal.
    """
    filtered_pixels = _filter_extreme_pixels(lab_pixels)

    if len(filtered_pixels) < 15:
        # Jika hampir semua piksel terbuang karena terlalu putih/gelap
        raise InvalidImageError(
            "Objek pakaian tidak terdeteksi dengan jelas (seluruh warna berupa latar putih/hitam pekat atau silau). "
            "Silakan ambil ulang foto objek pakaian dengan latar belakang netral."
        )

    k_actual = min(k, len(filtered_pixels))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 0.5)

    _, labels, centers = cv2.kmeans(
        filtered_pixels.astype(np.float32),
        k_actual,
        None,
        criteria,
        attempts=3,
        flags=cv2.KMEANS_PP_CENTERS,
    )

    counts = np.bincount(labels.flatten())
    dominant_idx = int(np.argmax(counts))
    dominant_lab = centers[dominant_idx]

    return float(dominant_lab[0]), float(dominant_lab[1]), float(dominant_lab[2])


def process_quick_detection(image_bytes: bytes) -> str:
    """Mode Cepat untuk POST /api/detect (kamera real-time).
    
    Spesifikasi Revisi:
    - Crop tengah (area 60% tengah)
    - Resize kecil (96 px)
    - K-Means di ruang CIELAB saja tanpa GrabCut (harus cepat)
    - Mengembalikan kode HEX '#RRGGBB'
    """
    img = validate_and_decode_image(image_bytes)

    # 1. Resize kecil (maksimal 96 px)
    small = _resize_longest_side(img, max_dim=96)
    h, w = small.shape[:2]

    # 2. Crop area tengah (60% tengah)
    margin_y = max(1, int(h * 0.20))
    margin_x = max(1, int(w * 0.20))
    center_crop = small[margin_y:h - margin_y, margin_x:w - margin_x]
    if center_crop.size == 0:
        center_crop = small

    # 3. Konversi ke ruang CIELAB
    lab_crop = _bgr_to_cielab_float(center_crop)
    lab_pixels = lab_crop.reshape(-1, 3)

    # 4. K-Means di ruang CIELAB dengan eliminasi ekstrem
    L, a, b = _kmeans_dominant_lab(lab_pixels, k=2)

    # 5. Konversi Lab kembali ke RGB -> HEX
    r, g, b_val = lab_to_rgb(L, a, b)
    return rgb_to_hex(r, g, b_val)


def process_clothing_analysis(image_bytes: bytes) -> Tuple[int, int, int]:
    """Mode Lengkap untuk POST /api/analyze.
    
    Spesifikasi Revisi:
    1. Validasi gambar (MIME, decode, batas 5MB, maks 4096 px)
    2. Resize: sisi terpanjang maksimal 640 px
    3. Gaussian Blur untuk memperhalus noise
    4. GrabCut dengan bounding box rect di tengah (margin 15%)
    5. Fallback ke crop tengah jika piksel foreground < 5% dari total area
    6. K-Means di ruang CIELAB pada piksel foreground yang bukan hampir putih/hitam
    7. Kembalikan (r, g, b) dari klaster dominan
    """
    img = validate_and_decode_image(image_bytes)

    # 1. Resize dengan sisi terpanjang maksimal 640 px
    resized = _resize_longest_side(img, max_dim=640)
    h, w = resized.shape[:2]

    # 2. Gaussian Blur untuk mengurangi noise tekstur
    blurred = cv2.GaussianBlur(resized, (5, 5), sigmaX=0)

    # 3. GrabCut Segmentation
    margin_x = max(2, int(w * 0.15))
    margin_y = max(2, int(h * 0.15))
    rect_w = max(10, w - (2 * margin_x))
    rect_h = max(10, h - (2 * margin_y))
    rect = (margin_x, margin_y, rect_w, rect_h)

    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    use_fallback = False
    try:
        cv2.grabCut(blurred, mask, rect, bgd_model, fgd_model, iterCount=3, mode=cv2.GC_INIT_WITH_RECT)
        fg_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype('uint8')
        total_fg_pixels = int(np.sum(fg_mask))

        # Fallback bila foreground terlalu kecil (< 5% dari total area)
        if total_fg_pixels < (0.05 * h * w):
            logger.info("GrabCut foreground terlalu kecil (<5%%), beralih ke fallback crop tengah.")
            use_fallback = True
    except Exception as e:
        logger.warning(f"GrabCut gagal ({e}), beralih ke fallback crop tengah.")
        use_fallback = True

    # 4. Fallback ke crop area tengah
    if use_fallback:
        fg_mask = np.zeros((h, w), np.uint8)
        c_y1, c_y2 = int(h * 0.25), int(h * 0.75)
        c_x1, c_x2 = int(w * 0.25), int(w * 0.75)
        fg_mask[c_y1:c_y2, c_x1:c_x2] = 1

    # 5. Konversi citra ke CIELAB dan ambil piksel foreground
    lab_img = _bgr_to_cielab_float(resized)
    fg_lab_pixels = lab_img[fg_mask == 1]

    if len(fg_lab_pixels) < 20:
        raise InvalidImageError(
            "Segmentasi pakaian tidak mendeteksi objek foreground. "
            "Pastikan pakaian berada di tengah frame kamera."
        )

    # 6. K-Means clustering di ruang warna CIELAB
    L, a, b = _kmeans_dominant_lab(fg_lab_pixels, k=3)

    # 7. Konversi ke RGB dan validasi hasil
    r, g, b_val = lab_to_rgb(L, a, b)
    _, s_val, v_val = rgb_to_hsv(r, g, b_val)

    if v_val < 0.04:
        raise InvalidImageError(
            "Warna pakaian terdeteksi terlalu gelap atau hitam pekat tanpa detail. Pastikan pencahayaan cukup."
        )

    return r, g, b_val
