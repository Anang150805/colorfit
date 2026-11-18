"""Color Harmony Service.

Menentukan jenis harmoni warna berdasarkan selisih sudut hue pada lingkaran warna Johannes Itten:
- Monochromatic (<~15°)
- Analogous (~30°, toleransi ±15°: 15° - 45°)
- Accent Contrast (rentang transisi: 45° - 105°)
- Triadic (~120°, toleransi ±15°: 105° - 135°)
- Split Complementary (~150°, toleransi ±15°: 135° - 165°)
- Complementary (~180°, toleransi ±15°: 165° - 180°)
- Netral (bila salah satu warna memiliki saturation < 0.12 atau value < 0.12)
"""

from typing import Tuple


def calculate_hue_distance(h1: float, h2: float) -> float:
    """Menghitung selisih sudut terkecil melingkar pada lingkaran warna (0 - 180 derajat).
    
    Formula: min(abs(h1 - h2) % 360, 360 - (abs(h1 - h2) % 360))
    """
    diff = abs(float(h1) - float(h2)) % 360.0
    return min(diff, 360.0 - diff)


def is_neutral_color(s: float, v: float) -> bool:
    """Memeriksa apakah warna tergolong netral: saturation < 0.12 atau value < 0.12."""
    return float(s) < 0.12 or float(v) < 0.12


def determine_harmony(
    h1: float, s1: float, v1: float,
    h2: float, s2: float, v2: float
) -> Tuple[str, str]:
    """Menentukan jenis harmoni warna dan penjelasan singkat berbahasa Indonesia.
    
    Args:
        h1, s1, v1: HSV warna terdeteksi (H: 0-360, S: 0-1, V: 0-1).
        h2, s2, v2: HSV warna kombinasi (H: 0-360, S: 0-1, V: 0-1).
        
    Returns:
        Tuple[str, str]: (nama_harmoni, penjelasan_bahasa_indonesia).
    """
    # 1. Periksa warna netral (saturation < 0.12 atau value < 0.12)
    if is_neutral_color(s1, v1) or is_neutral_color(s2, v2):
        return (
            "Netral",
            "Warna netral memberikan keseimbangan visual yang elegan, tenang, dan serasi dipadukan dengan hampir semua warna."
        )

    # 2. Hitung selisih sudut hue melingkar
    diff = calculate_hue_distance(h1, h2)

    # 3. Klasifikasi berdasarkan toleransi ±15 derajat
    if diff <= 15.0:
        return (
            "Monochromatic",
            "Kombinasi warna senada dari rumpun warna yang sama, memberikan kesan rapi, minimalis, dan elegan."
        )
    elif 15.0 < diff <= 45.0:
        return (
            "Analogous",
            "Kombinasi warna yang bersebelahan pada roda warna (~30°), menciptakan tampilan yang selaras dan tenang."
        )
    elif 45.0 < diff <= 105.0:
        return (
            "Accent Contrast",
            "Kombinasi kontras sedang yang memberikan aksen visual segar dan dinamis namun tetap serasi."
        )
    elif 105.0 < diff <= 135.0:
        return (
            "Triadic",
            "Kombinasi tiga sudut roda warna (~120°) yang seimbang, ceria, dan kaya akan variasi visual."
        )
    elif 135.0 < diff <= 165.0:
        return (
            "Split Complementary",
            "Kombinasi kontras cabang komplementer (~150°) yang berkarakter dan menarik tanpa terasa terlalu tajam."
        )
    else:  # 165.0 < diff <= 180.0
        return (
            "Complementary",
            "Kombinasi warna berseberangan (~180°) dengan kontras tinggi, memberikan kesan tegas, berani, dan memikat."
        )
