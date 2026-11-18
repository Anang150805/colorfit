"""Pengujian Unit dan Integrasi API ColorFit (pytest & Flask Test Client).

Mencakup pengujian untuk:
1. Endpoint /health
2. Endpoint /api/classify (valid, invalid undertone, non-JSON)
3. Endpoint /api/detect (gambar normal, gambar rusak, gambar hilang)
4. Endpoint /api/analyze (gambar pakaian normal, undertone invalid, gambar gelap, gambar silau, gambar rusak)
5. Modul pendukung (color_features & color_harmony)
"""

import io
import os
import sys
import pytest
import numpy as np
import cv2

# Pastikan direktori root backend terdaftar di sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TEST_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app
from services.color_features import (
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_to_lab,
    lab_to_rgb
)
from services.color_harmony import determine_harmony, calculate_hue_distance


@pytest.fixture
def client():
    """Fixture Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def create_synthetic_image_bytes(
    width: int = 150,
    height: int = 150,
    color_bgr: tuple = (14, 65, 183),  # Terracotta / Merah Bata dalam BGR
    add_margin: bool = True
) -> bytes:
    """Membangkitkan gambar sintetis dalam format PNG bytes di memori."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    if add_margin:
        # Berikan background abu-abu netral dengan objek berwarna di tengah
        img[:, :] = (200, 200, 200)
        # Objek pakaian di tengah
        y1, y2 = int(height * 0.2), int(height * 0.8)
        x1, x2 = int(width * 0.2), int(width * 0.8)
        img[y1:y2, x1:x2] = color_bgr
    else:
        img[:, :] = color_bgr

    success, encoded_img = cv2.imencode(".png", img)
    assert success, "Gagal meng-encode citra sintetis ke PNG"
    return encoded_img.tobytes()


# ==============================================================================
# 1. PENGUJIAN HEALTH CHECK
# ==============================================================================
def test_health_check(client):
    """Memastikan endpoint /health merespons status OK 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "ColorFit" in data["message"]


# ==============================================================================
# 2. PENGUJIAN /api/classify
# ==============================================================================
@pytest.mark.parametrize("undertone", ["warm", "cool", "neutral"])
def test_classify_valid(client, undertone):
    """Menguji POST /api/classify dengan undertone yang valid."""
    response = client.post(
        "/api/classify",
        json={"undertone": undertone}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["undertone"] == undertone
    assert isinstance(data["colors"], list)
    assert len(data["colors"]) > 0

    valid_suitabilities = {"Sangat Cocok", "Cocok", "Kurang Cocok"}
    valid_families = {"merah", "kuning", "hijau", "biru", "ungu", "oranye", "pink", "coklat", "netral"}

    for color in data["colors"]:
        assert "name" in color
        assert "hex" in color
        assert color["hex"].startswith("#")
        assert "family" in color
        assert color["family"] in valid_families
        assert "suitability" in color
        assert color["suitability"] in valid_suitabilities


def test_classify_invalid_undertone(client):
    """Menguji POST /api/classify dengan undertone tidak valid."""
    response = client.post(
        "/api/classify",
        json={"undertone": "alien_undertone"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "tidak valid" in data["message"].lower()


def test_classify_missing_body(client):
    """Menguji POST /api/classify tanpa payload JSON."""
    response = client.post(
        "/api/classify",
        data="bukan json",
        content_type="text/plain"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


# ==============================================================================
# 3. PENGUJIAN /api/detect
# ==============================================================================
def test_detect_valid_image(client):
    """Menguji POST /api/detect dengan frame kamera sintetis."""
    # Warna biru navy BGR: (128, 0, 0)
    image_bytes = create_synthetic_image_bytes(80, 80, (128, 0, 0), add_margin=False)

    data = {
        "image": (io.BytesIO(image_bytes), "camera_frame.png")
    }
    response = client.post(
        "/api/detect",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    result = response.get_json()
    assert result["success"] is True
    assert "hex" in result
    assert result["hex"].startswith("#")
    assert len(result["hex"]) == 7


def test_detect_missing_image(client):
    """Menguji POST /api/detect tanpa menyertakan field gambar."""
    response = client.post(
        "/api/detect",
        data={},
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    result = response.get_json()
    assert result["success"] is False
    assert "image" in result["message"].lower()


def test_detect_corrupt_image(client):
    """Menguji POST /api/detect dengan byte gambar rusak."""
    corrupt_bytes = b"bukan data gambar valid"
    data = {
        "image": (io.BytesIO(corrupt_bytes), "broken.png")
    }
    response = client.post(
        "/api/detect",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    result = response.get_json()
    assert result["success"] is False


# ==============================================================================
# 4. PENGUJIAN /api/analyze
# ==============================================================================
def test_analyze_valid_clothing(client):
    """Menguji POST /api/analyze dengan gambar pakaian sintetis dan undertone warm."""
    # BGR (14, 65, 183) -> RGB (183, 65, 14) Merah Bata
    img_bytes = create_synthetic_image_bytes(200, 200, (14, 65, 183), add_margin=True)

    data = {
        "image": (io.BytesIO(img_bytes), "shirt.png"),
        "undertone": "warm"
    }
    response = client.post(
        "/api/analyze",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    result = response.get_json()
    assert result["success"] is True

    # Periksa detected color representations
    detected = result["detected"]
    assert "hex" in detected
    assert detected["hex"].startswith("#")
    assert "rgb" in detected and len(detected["rgb"]) == 3
    assert "hsv" in detected and len(detected["hsv"]) == 3
    assert "lab" in detected and len(detected["lab"]) == 3

    # Periksa kesesuaian (suitability)
    assert result["suitability"] in ["Sangat Cocok", "Cocok", "Kurang Cocok"]

    # Periksa rekomendasi padu-padan
    recommendations = result["recommendations"]
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    for rec in recommendations:
        assert "name" in rec
        assert "hex" in rec
        assert rec["hex"].startswith("#")
        assert "harmony" in rec
        assert "explanation" in rec
        assert "distance" in rec
        assert isinstance(rec["distance"], (int, float))
        assert "suitability" in rec
        assert rec["suitability"] in ["Sangat Cocok", "Cocok", "Kurang Cocok"]

    assert result["message"] is None


def test_analyze_invalid_undertone(client):
    """Menguji POST /api/analyze dengan field undertone tidak valid."""
    img_bytes = create_synthetic_image_bytes(100, 100, (50, 100, 50))
    data = {
        "image": (io.BytesIO(img_bytes), "sample.png"),
        "undertone": "invalid_tone"
    }
    response = client.post(
        "/api/analyze",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    result = response.get_json()
    assert result["success"] is False
    assert "undertone" in result["message"].lower()


def test_analyze_pitch_black_image(client):
    """Menguji POST /api/analyze dengan gambar yang terlalu gelap (underexposed)."""
    # Citra hitam pekat (all 0)
    black_img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".png", black_img)
    black_bytes = encoded.tobytes()

    data = {
        "image": (io.BytesIO(black_bytes), "dark.png"),
        "undertone": "warm"
    }
    response = client.post(
        "/api/analyze",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    result = response.get_json()
    assert result["success"] is False
    assert "gelap" in result["message"].lower()


def test_analyze_overexposed_image(client):
    """Menguji POST /api/analyze dengan gambar yang overexposed/silau total."""
    # Citra putih pekat (all 255)
    white_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    _, encoded = cv2.imencode(".png", white_img)
    white_bytes = encoded.tobytes()

    data = {
        "image": (io.BytesIO(white_bytes), "white.png"),
        "undertone": "cool"
    }
    response = client.post(
        "/api/analyze",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    result = response.get_json()
    assert result["success"] is False
    assert ("terang" in result["message"].lower() or "silau" in result["message"].lower() or "kontras" in result["message"].lower())


# ==============================================================================
# 5. PENGUJIAN MODUL COLOR FEATURES & HARMONY
# ==============================================================================
def test_color_conversions_consistency():
    """Menguji konsistensi dan batas skala konversi HEX, RGB, HSV, CIELAB."""
    hex_code = "#B7410E"
    r, g, b = hex_to_rgb(hex_code)
    assert (r, g, b) == (183, 65, 14)
    assert rgb_to_hex(r, g, b) == hex_code

    h, s, v = rgb_to_hsv(r, g, b)
    assert 0.0 <= h <= 360.0
    assert 0.0 <= s <= 1.0
    assert 0.0 <= v <= 1.0

    L, a_val, b_val = rgb_to_lab(r, g, b)
    assert 0.0 <= L <= 100.0
    assert -128.0 <= a_val <= 127.0
    assert -128.0 <= b_val <= 127.0


def test_color_harmony_rules():
    """Menguji aturan harmoni warna Itten."""
    # Monochromatic (selisih < 15)
    harm, exp = determine_harmony(20.0, 0.8, 0.8, 25.0, 0.8, 0.8)
    assert harm == "Monochromatic"
    assert len(exp) > 0

    # Analogous (~30)
    harm, _ = determine_harmony(30.0, 0.8, 0.8, 60.0, 0.8, 0.8)
    assert harm == "Analogous"

    # Complementary (~180)
    harm, _ = determine_harmony(10.0, 0.8, 0.8, 190.0, 0.8, 0.8)
    assert harm == "Complementary"

    # Neutral Harmony (warna dengan saturasi rendah)
    harm, exp = determine_harmony(10.0, 0.8, 0.8, 200.0, 0.05, 0.8)
    assert harm == "Neutral Harmony"
