"""Decision Tree Service ColorFit.

Memuat model Decision Tree SEKALI (singleton) saat startup server.
Menyediakan:
1. predict_suitability(undertone, h, s, v): Memprediksi kesesuaian warna ('Sangat Cocok', 'Cocok', 'Kurang Cocok')
   menggunakan 7 fitur terintegrasi (one-hot undertone, hue_sin, hue_cos, saturation, value).
2. classify_palette(undertone): Mengambil dan memprediksi palet warna lengkap untuk POST /api/classify.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.color_features import extract_decision_tree_features

logger = logging.getLogger("colorfit.decision_tree_service")

MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(MODELS_DIR, "decision_tree.pkl")
COLORS_CSV_PATH = os.path.join(DATA_DIR, "colors.csv")

_model_bundle: Optional[Dict[str, Any]] = None
_colors_df_cache: Optional[pd.DataFrame] = None


def load_model() -> Dict[str, Any]:
    """Memuat bundle model Decision Tree sekali saat startup server."""
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle

    if os.path.exists(MODEL_PATH):
        logger.info(f"Memuat model Decision Tree dari: {MODEL_PATH}")
        _model_bundle = joblib.load(MODEL_PATH)
    else:
        logger.warning(f"File {MODEL_PATH} tidak ditemukan, melatih model otomatis...")
        from train_model import train_decision_tree
        if not os.path.exists(COLORS_CSV_PATH):
            from scripts.build_dataset import build_colors_dataframe
            df = build_colors_dataframe()
            os.makedirs(DATA_DIR, exist_ok=True)
            df.to_csv(COLORS_CSV_PATH, index=False)
        else:
            df = pd.read_csv(COLORS_CSV_PATH)

        _model_bundle = train_decision_tree(df)
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(_model_bundle, MODEL_PATH)

    return _model_bundle


def _get_colors_df() -> pd.DataFrame:
    """Memuat cache dataframe colors.csv."""
    global _colors_df_cache
    if _colors_df_cache is not None:
        return _colors_df_cache

    if not os.path.exists(COLORS_CSV_PATH):
        from scripts.build_dataset import build_colors_dataframe
        os.makedirs(DATA_DIR, exist_ok=True)
        _colors_df_cache = build_colors_dataframe()
        _colors_df_cache.to_csv(COLORS_CSV_PATH, index=False)
    else:
        _colors_df_cache = pd.read_csv(COLORS_CSV_PATH)

    return _colors_df_cache


def predict_suitability(undertone: str, h: float, s: float, v: float) -> str:
    """Memprediksi tingkat kesesuaian warna pakaian terhadap undertone pengguna.
    
    Args:
        undertone: 'warm', 'cool', atau 'neutral'.
        h: Hue dalam derajat [0.0, 360.0].
        s: Saturation [0.0, 1.0].
        v: Value / Kecerahan [0.0, 1.0].
        
    Returns:
        str: Salah satu dari 'Sangat Cocok', 'Cocok', atau 'Kurang Cocok'.
    """
    undertone_clean = undertone.strip().lower()
    if undertone_clean not in ["warm", "cool", "neutral"]:
        raise ValueError(f"Undertone '{undertone}' tidak valid. Pilihan: warm, cool, neutral.")

    bundle = load_model()
    clf = bundle["model"]

    # Ekstrak 7 fitur identik dengan training
    features = extract_decision_tree_features(undertone_clean, h, s, v)
    prediction = clf.predict([features])[0]
    return str(prediction)


def classify_palette(undertone: str) -> List[Dict[str, str]]:
    """Mengembalikan daftar rekomendasi palet warna untuk POST /api/classify.
    
    Args:
        undertone: 'warm', 'cool', atau 'neutral'.
        
    Returns:
        List[Dict[str, str]]: Koleksi warna dengan name, hex, family, dan suitability.
    """
    undertone_clean = undertone.strip().lower()
    if undertone_clean not in ["warm", "cool", "neutral"]:
        raise ValueError(f"Undertone '{undertone}' tidak valid. Pilihan: warm, cool, neutral.")

    df = _get_colors_df()
    subset = df[df["undertone"].str.lower() == undertone_clean].copy()
    if subset.empty:
        subset = df.copy()

    results = []
    for _, row in subset.iterrows():
        name = str(row["name"])
        hex_code = str(row["hex"]).upper()
        family = str(row["family"]).lower()
        h = float(row["hue"])
        s = float(row["saturation"])
        v = float(row["value"])

        suitability = predict_suitability(undertone_clean, h, s, v)

        results.append({
            "name": name,
            "hex": hex_code,
            "family": family,
            "suitability": suitability
        })

    return results
