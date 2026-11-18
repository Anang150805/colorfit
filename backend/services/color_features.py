"""Color Features Service.

Modul ini bertanggung jawab untuk konversi ruang warna:
- HEX (#RRGGBB)
- RGB: [0, 255]
- HSV:
    - Hue (H): [0.0, 360.0] derajat
    - Saturation (S): [0.0, 1.0]
    - Value (V): [0.0, 1.0]
- CIELAB (D65 Standard Illuminant):
    - L* (Kecerahan): [0.0, 100.0]
    - a* (Komponen hijau - merah): [-128.0, 127.0]
    - b* (Komponen biru - kuning): [-128.0, 127.0]

Semua skala di atas dijaga konsisten di seluruh modul backend ColorFit.
"""

from typing import Tuple, Dict, Any, List
import colorsys
import math
import numpy as np

# Daftar Nama Fitur Decision Tree (Konsisten untuk Training & Inferensi)
DT_FEATURE_NAMES = [
    "undertone_warm",
    "undertone_cool",
    "undertone_neutral",
    "hue_sin",
    "hue_cos",
    "saturation",
    "value",
]


def extract_decision_tree_features(
    undertone: str, h: float, s: float, v: float
) -> List[float]:
    """Mengekstrak 7 fitur untuk model Decision Tree ColorFit.
    
    Fitur:
    1. undertone_warm: 1 jika warm, 0 lainnya (one-hot)
    2. undertone_cool: 1 jika cool, 0 lainnya (one-hot)
    3. undertone_neutral: 1 jika neutral, 0 lainnya (one-hot)
    4. hue_sin: sin(hue dalam radian) untuk merepresentasikan sifat melingkar hue
    5. hue_cos: cos(hue dalam radian) untuk merepresentasikan sifat melingkar hue
    6. saturation: nilai saturasi [0.0, 1.0]
    7. value: nilai kecerahan / value [0.0, 1.0]
    
    Returns:
        List[float]: Vector 7 fitur numerik.
    """
    u = str(undertone).strip().lower()
    is_warm = 1.0 if u == "warm" else 0.0
    is_cool = 1.0 if u == "cool" else 0.0
    is_neutral = 1.0 if u == "neutral" else 0.0

    # Konversi sudut hue (0-360 derajat) ke radian
    h_rad = math.radians(float(h) % 360.0)
    h_sin = round(math.sin(h_rad), 6)
    h_cos = round(math.cos(h_rad), 6)

    s_clamped = max(0.0, min(1.0, float(s)))
    v_clamped = max(0.0, min(1.0, float(v)))

    return [is_warm, is_cool, is_neutral, h_sin, h_cos, s_clamped, v_clamped]


# Konstanta Referensi White Point D65 (Standar CIE 1931, observer 2 derajat)
D65_XN = 95.0489
D65_YN = 100.0000
D65_ZN = 108.8840

DELTA_LAB = 6.0 / 29.0
DELTA_CUBE = DELTA_LAB ** 3  # ~0.008856451679


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Mengonversi kode warna HEX (misal '#RRGGBB' atau 'RRGGBB') menjadi tuple RGB (0-255).
    
    Args:
        hex_str: String format hex (#A1B2C3 atau A1B2C3).
        
    Returns:
        Tuple (r, g, b) bertipe integer dalam rentang [0, 255].
    """
    clean_hex = hex_str.strip().lstrip('#')
    if len(clean_hex) != 6:
        raise ValueError(f"Format HEX tidak valid: {hex_str}. Harus 6 karakter heksadesimal.")
    r = int(clean_hex[0:2], 16)
    g = int(clean_hex[2:4], 16)
    b = int(clean_hex[4:6], 16)
    return r, g, b


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Mengonversi nilai RGB (0-255) menjadi string HEX kapital (misal '#RRGGBB').
    
    Args:
        r: Nilai merah (0-255).
        g: Nilai hijau (0-255).
        b: Nilai biru (0-255).
        
    Returns:
        String HEX '#RRGGBB'.
    """
    r_clamped = max(0, min(255, int(round(r))))
    g_clamped = max(0, min(255, int(round(g))))
    b_clamped = max(0, min(255, int(round(b))))
    return f"#{r_clamped:02X}{g_clamped:02X}{b_clamped:02X}"


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Mengonversi nilai RGB (0-255) ke HSV.
    
    Skala output:
    - Hue (h): 0.0 - 360.0 derajat
    - Saturation (s): 0.0 - 1.0
    - Value (v): 0.0 - 1.0
    
    Args:
        r, g, b: Komponen warna dalam rentang [0, 255].
        
    Returns:
        Tuple (h, s, v).
    """
    r_norm = max(0.0, min(1.0, r / 255.0))
    g_norm = max(0.0, min(1.0, g / 255.0))
    b_norm = max(0.0, min(1.0, b / 255.0))

    h_norm, s_norm, v_norm = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    h_deg = h_norm * 360.0
    return round(h_deg, 2), round(s_norm, 4), round(v_norm, 4)


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Mengonversi nilai HSV ke RGB (0-255).
    
    Skala input:
    - Hue (h): 0.0 - 360.0 derajat
    - Saturation (s): 0.0 - 1.0
    - Value (v): 0.0 - 1.0
    
    Returns:
        Tuple (r, g, b) dalam rentang [0, 255].
    """
    h_norm = (h % 360.0) / 360.0
    s_norm = max(0.0, min(1.0, s))
    v_norm = max(0.0, min(1.0, v))

    r_norm, g_norm, b_norm = colorsys.hsv_to_rgb(h_norm, s_norm, v_norm)
    return int(round(r_norm * 255)), int(round(g_norm * 255)), int(round(b_norm * 255))


def _srgb_to_linear(c: float) -> float:
    """Mengonversi nilai sRGB gamma-corrected [0, 1] ke sRGB linear [0, 1]."""
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    """Mengonversi nilai sRGB linear [0, 1] ke sRGB gamma-corrected [0, 1]."""
    if c <= 0.0031308:
        return c * 12.92
    return 1.055 * (c ** (1.0 / 2.4)) - 0.055


def _f_lab(t: float) -> float:
    """Fungsi transfer non-linear CIE XYZ ke CIELAB."""
    if t > DELTA_CUBE:
        return t ** (1.0 / 3.0)
    return (t / (3.0 * (DELTA_LAB ** 2))) + (4.0 / 29.0)


def _f_lab_inv(t: float) -> float:
    """Invers fungsi transfer non-linear CIELAB ke CIE XYZ."""
    if t > DELTA_LAB:
        return t ** 3.0
    return 3.0 * (DELTA_LAB ** 2) * (t - 4.0 / 29.0)


def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Mengonversi nilai RGB (0-255) ke ruang warna CIELAB (D65).
    
    Skala output:
    - L* (Kecerahan): 0.0 - 100.0
    - a* (Hijau ke Merah): -128.0 - 127.0
    - b* (Biru ke Kuning): -128.0 - 127.0
    
    Returns:
        Tuple (L, a, b).
    """
    # 1. Normalisasi sRGB dan linearisasi (kompensasi gamma)
    r_lin = _srgb_to_linear(max(0.0, min(1.0, r / 255.0)))
    g_lin = _srgb_to_linear(max(0.0, min(1.0, g / 255.0)))
    b_lin = _srgb_to_linear(max(0.0, min(1.0, b / 255.0)))

    # 2. Konversi sRGB linear ke CIE XYZ (D65)
    X = (0.4124564 * r_lin + 0.3575761 * g_lin + 0.1804375 * b_lin) * 100.0
    Y = (0.2126729 * r_lin + 0.7151522 * g_lin + 0.0721750 * b_lin) * 100.0
    Z = (0.0193339 * r_lin + 0.1191920 * g_lin + 0.9503041 * b_lin) * 100.0

    # 3. Konversi CIE XYZ ke CIELAB menggunakan D65 reference white point
    fx = _f_lab(X / D65_XN)
    fy = _f_lab(Y / D65_YN)
    fz = _f_lab(Z / D65_ZN)

    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b_val = 200.0 * (fy - fz)

    return round(L, 2), round(a, 2), round(b_val, 2)


def lab_to_rgb(L: float, a: float, b_val: float) -> Tuple[int, int, int]:
    """Mengonversi nilai CIELAB (D65) kembali ke nilai RGB (0-255).
    
    Returns:
        Tuple (r, g, b).
    """
    fy = (L + 16.0) / 116.0
    fx = (a / 500.0) + fy
    fz = fy - (b_val / 200.0)

    X = D65_XN * _f_lab_inv(fx) / 100.0
    Y = D65_YN * _f_lab_inv(fy) / 100.0
    Z = D65_ZN * _f_lab_inv(fz) / 100.0

    # Invers matriks XYZ ke sRGB linear
    r_lin = 3.2404542 * X - 1.5371385 * Y - 0.4985314 * Z
    g_lin = -0.9692660 * X + 1.8760108 * Y + 0.0415560 * Z
    b_lin = 0.0556434 * X - 0.2040259 * Y + 1.0572252 * Z

    r = int(round(_linear_to_srgb(max(0.0, min(1.0, r_lin))) * 255.0))
    g = int(round(_linear_to_srgb(max(0.0, min(1.0, g_lin))) * 255.0))
    b = int(round(_linear_to_srgb(max(0.0, min(1.0, b_lin))) * 255.0))

    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))


def hex_to_hsv(hex_str: str) -> Tuple[float, float, float]:
    """Helper langsung dari HEX ke HSV (H: 0-360, S: 0-1, V: 0-1)."""
    r, g, b = hex_to_rgb(hex_str)
    return rgb_to_hsv(r, g, b)


def hex_to_lab(hex_str: str) -> Tuple[float, float, float]:
    """Helper langsung dari HEX ke CIELAB (L: 0-100, a: -128..127, b: -128..127)."""
    r, g, b = hex_to_rgb(hex_str)
    return rgb_to_lab(r, g, b)


def get_all_color_representations(r: int, g: int, b: int) -> Dict[str, Any]:
    """Mengembalikan representasi lengkap warna untuk respons API ColorFit.
    
    Struktur hasil sesuai kontrak API:
    {
        "hex": "#RRGGBB",
        "rgb": [r, g, b],
        "hsv": [h, s, v],
        "lab": [L, a, b]
    }
    """
    hex_code = rgb_to_hex(r, g, b)
    h, s, v = rgb_to_hsv(r, g, b)
    L, a_val, b_val = rgb_to_lab(r, g, b)

    return {
        "hex": hex_code,
        "rgb": [int(r), int(g), int(b)],
        "hsv": [h, s, v],
        "lab": [L, a_val, b_val],
    }
