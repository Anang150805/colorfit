"""Route Classify: POST /api/classify.

Menyediakan daftar palet warna beserta tingkat kesesuaiannya terhadap undertone pengguna
(warm, cool, neutral) menggunakan model Decision Tree (7 fitur).
"""

import logging
from flask import Blueprint, request, jsonify
from services.decision_tree_service import classify_palette

logger = logging.getLogger("colorfit.routes.classify")
classify_bp = Blueprint("classify", __name__)


@classify_bp.route("/classify", methods=["POST"])
def classify():
    """POST /api/classify
    
    Request JSON:
        {"undertone": "warm" | "cool" | "neutral"}
    """
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Format request tidak valid. Request body harus berupa JSON."
        }), 400

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body JSON kosong atau format tidak valid."
        }), 400

    undertone = data.get("undertone")
    if not undertone or not isinstance(undertone, str):
        return jsonify({
            "success": False,
            "message": "Field 'undertone' wajib diisi (string: warm, cool, atau neutral)."
        }), 400

    undertone_clean = undertone.strip().lower()
    if undertone_clean not in ["warm", "cool", "neutral"]:
        return jsonify({
            "success": False,
            "message": f"Undertone '{undertone}' tidak valid. Pilihan: warm, cool, neutral."
        }), 400

    try:
        colors = classify_palette(undertone_clean)
        return jsonify({
            "success": True,
            "undertone": undertone_clean,
            "colors": colors
        }), 200
    except Exception as e:
        logger.error(f"Kesalahan pada classify: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Terjadi kesalahan saat memproses klasifikasi palet: {str(e)}"
        }), 500
