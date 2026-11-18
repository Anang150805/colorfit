"""Route Detect: POST /api/detect.

Mode cepat untuk mendeteksi warna dominan dari frame kamera real-time (K-Means ruang CIELAB).
"""

import logging
from flask import Blueprint, request, jsonify
from services.image_processing import process_quick_detection, InvalidImageError

logger = logging.getLogger("colorfit.routes.detect")
detect_bp = Blueprint("detect", __name__)


@detect_bp.route("/detect", methods=["POST"])
def detect():
    """POST /api/detect
    
    Request multipart/form-data:
        - field 'image': frame kamera citra (JPG/PNG).
        
    Response JSON:
        {"success": true, "hex": "#A1B2C3"}
    """
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

    image_bytes = file.read()
    if not image_bytes or len(image_bytes) == 0:
        return jsonify({
            "success": False,
            "message": "File gambar kosong atau byte data tidak terbaca."
        }), 400

    try:
        hex_color = process_quick_detection(image_bytes)
        return jsonify({
            "success": True,
            "hex": hex_color
        }), 200
    except InvalidImageError as e:
        logger.warning(f"Deteksi cepat gagal: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Kesalahan tidak terduga pada /api/detect: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Terjadi kesalahan saat mendeteksi warna: {str(e)}"
        }), 500
