"""Route Analyze: POST /api/analyze.

Revisi Alur Rekomendasi:
1. Validasi gambar (MIME, decode cv2.imdecode, ukuran <= 5MB, batas dimensi maks).
2. Segmentasi pakaian (GrabCut + fallback crop tengah) & K-Means di ruang CIELAB.
3. Ambil K tetangga terdekat dari model KNN (NearestNeighbors CIELAB Euclidean).
4. Kumpulkan combo_hex dari tiap tetangga dan hapus duplikat.
5. Nilai tiap kombinasi pakaian dengan Decision Tree terhadap undertone pengguna.
6. Urutkan berdasarkan prioritas: Sangat Cocok > Cocok > Kurang Cocok, lalu berdasarkan jarak Euclidean terkecil.
7. Ambil maksimal 5 rekomendasi.
8. Menambahkan field 'suitability' pada tiap objek rekomendasi.
"""

import logging
from flask import Blueprint, request, jsonify
from services.image_processing import process_clothing_analysis, InvalidImageError
from services.color_features import get_all_color_representations, hex_to_hsv
from services.decision_tree_service import predict_suitability
from services.knn_service import find_combinations
from services.color_harmony import determine_harmony

logger = logging.getLogger("colorfit.routes.analyze")
analyze_bp = Blueprint("analyze", __name__)

# Konstanta Pengambilan Tetangga & Batas Rekomendasi
KNN_QUERY_K = 12
MAX_RECOMMENDATIONS = 5

SUITABILITY_PRIORITY = {
    "Sangat Cocok": 0,
    "Cocok": 1,
    "Kurang Cocok": 2
}


@analyze_bp.route("/analyze", methods=["POST"])
def analyze():
    """POST /api/analyze
    
    Request multipart/form-data:
        - field 'image': file gambar pakaian (JPG/PNG).
        - field 'undertone': 'warm' | 'cool' | 'neutral'.
    """
    # 1. Validasi keberadaan file gambar
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "Field 'image' tidak ditemukan dalam request multipart."
        }), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({
            "success": False,
            "message": "File gambar tidak boleh kosong."
        }), 400

    # 2. Validasi field undertone
    undertone_raw = request.form.get("undertone")
    if not undertone_raw or not undertone_raw.strip():
        return jsonify({
            "success": False,
            "message": "Field form 'undertone' wajib diisi (warm, cool, neutral)."
        }), 400

    undertone = undertone_raw.strip().lower()
    if undertone not in ["warm", "cool", "neutral"]:
        return jsonify({
            "success": False,
            "message": f"Undertone '{undertone_raw}' tidak valid. Pilihan: warm, cool, neutral."
        }), 400

    # 3. Baca byte gambar
    image_bytes = file.read()
    if not image_bytes or len(image_bytes) == 0:
        return jsonify({
            "success": False,
            "message": "Data file gambar kosong."
        }), 400

    # 4. Pemrosesan citra pakaian (GrabCut + K-Means di ruang CIELAB)
    try:
        r, g, b = process_clothing_analysis(image_bytes)
    except InvalidImageError as e:
        logger.warning(f"Validasi citra pakaian gagal: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Kesalahan tidak terduga saat analisis citra: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Gagal menganalisis citra pakaian: {str(e)}"
        }), 500

    # 5. Representasi warna lengkap terdeteksi
    detected = get_all_color_representations(r, g, b)
    h_det, s_det, v_det = detected["hsv"]
    lab_det = detected["lab"]

    # 6. Prediksi kesesuaian warna terdeteksi dengan Decision Tree
    try:
        clothing_suitability = predict_suitability(undertone, h_det, s_det, v_det)
    except Exception as e:
        logger.warning(f"Prediksi kesesuaian gagal, fallback ke 'Cocok': {e}")
        clothing_suitability = "Cocok"

    # 7. Ambil K tetangga terdekat dari model KNN
    try:
        raw_combos = find_combinations(lab_det, k=KNN_QUERY_K)
    except Exception as e:
        logger.error(f"Gagal mencari paduan outfit via KNN: {e}")
        raw_combos = []

    # 8. Hapus duplikat combo_hex & nilai tiap kombinasi dengan Decision Tree
    unique_combos = []
    seen_hex = set()
    for item in raw_combos:
        c_hex = item["combo_hex"].upper()
        if c_hex not in seen_hex:
            seen_hex.add(c_hex)
            unique_combos.append(item)

    ranked_recommendations = []
    for item in unique_combos:
        c_hex = item["combo_hex"]
        h_combo, s_combo, v_combo = hex_to_hsv(c_hex)

        # Prediksi kesesuaian warna kombinasi bawahan/atasan dengan undertone pengguna
        try:
            combo_suitability = predict_suitability(undertone, h_combo, s_combo, v_combo)
        except Exception:
            combo_suitability = "Cocok"

        # Harmoni warna Itten
        harmony_type, explanation = determine_harmony(
            h_det, s_det, v_det,
            h_combo, s_combo, v_combo
        )

        ranked_recommendations.append({
            "name": item["combo_name"],
            "hex": c_hex,
            "harmony": harmony_type,
            "explanation": explanation,
            "distance": item["distance"],
            "suitability": combo_suitability
        })

    # 9. Urutkan prioritas: Sangat Cocok > Cocok > Kurang Cocok, lalu jarak terdekat
    ranked_recommendations.sort(
        key=lambda rec: (
            SUITABILITY_PRIORITY.get(rec["suitability"], 3),
            rec["distance"]
        )
    )

    # 10. Ambil maksimal 5 rekomendasi teratas
    final_recommendations = ranked_recommendations[:MAX_RECOMMENDATIONS]

    return jsonify({
        "success": True,
        "detected": detected,
        "suitability": clothing_suitability,
        "recommendations": final_recommendations,
        "message": None
    }), 200
