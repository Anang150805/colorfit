"""ColorFit Flask Application Entrypoint.

Backend API untuk rekomendasi padu-padan warna pakaian ColorFit.
Revisi Kualitas & Keamanan:
- Logging standar Python terkonfigurasi.
- Pre-loading model Machine Learning (Decision Tree & KNN) saat startup server.
- Default debug=False (hanya aktif jika FLASK_DEBUG=1 atau FLASK_DEBUG=true).
- Batas upload payload 5 MB.
- CORS aktif untuk komunikasi dengan Flutter mobile.
"""

import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Konfigurasi Logging Standar
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("colorfit.app")

from routes.classify import classify_bp
from routes.detect import detect_bp
from routes.analyze import analyze_bp
from services.decision_tree_service import load_model as preload_decision_tree
from services.knn_service import load_knn_model as preload_knn


def create_app() -> Flask:
    """Factory function untuk inisialisasi aplikasi Flask ColorFit."""
    app = Flask(__name__)

    # 1. Konfigurasi Batas Ukuran Upload: 5 MB
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.config["JSON_SORT_KEYS"] = False

    # 2. CORS diaktifkan untuk seluruh prefix /api/*
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 3. Pendaftaran Blueprint dengan prefix /api
    app.register_blueprint(classify_bp, url_prefix="/api")
    app.register_blueprint(detect_bp, url_prefix="/api")
    app.register_blueprint(analyze_bp, url_prefix="/api")

    # 4. Pre-load Model saat Startup Server (bukan per request)
    try:
        logger.info("Menginisialisasi dan memuat model Machine Learning saat startup...")
        preload_decision_tree()
        preload_knn()
        logger.info("Model Decision Tree & KNN berhasil dimuat ke memori.")
    except Exception as e:
        logger.warning(f"Model belum tersedia di disk saat inisialisasi startup ({e}). Akan dimuat otomatis saat request pertama.")

    # 5. Endpoint Health Check
    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint ColorFit."""
        return jsonify({
            "status": "ok",
            "message": "ColorFit backend is running"
        }), 200

    # 6. Error Handlers JSON Konsisten
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message": "Permintaan tidak valid (Bad Request)."
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Endpoint tidak ditemukan."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "message": "Metode HTTP tidak diizinkan pada endpoint ini."
        }), 405

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "message": "Ukuran file melebihi batas maksimum 5 MB."
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "message": "Terjadi kesalahan internal pada server ColorFit."
        }), 500

    return app


app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    # Default debug=False untuk keamanan produksi
    debug_env = os.environ.get("FLASK_DEBUG", "0").lower()
    debug = debug_env in ("true", "1")

    logger.info(f"Menjalankan server ColorFit pada http://{host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
