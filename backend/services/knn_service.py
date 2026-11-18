"""KNN (K-Nearest Neighbors) Service ColorFit.

Memuat model NearestNeighbors SEKALI (singleton) saat startup server.
Menyediakan pencarian kombinasi padu-padan pakaian serasi terdekat
berbasis jarak Euclidean dalam ruang warna CIELAB (L*, a*, b*).
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logger = logging.getLogger("colorfit.knn_service")

MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(MODELS_DIR, "knn.pkl")
OUTFITS_CSV_PATH = os.path.join(DATA_DIR, "outfits.csv")

_knn_bundle: Optional[Dict[str, Any]] = None


def load_knn_model() -> Dict[str, Any]:
    """Memuat bundle model KNN sekali saat startup server."""
    global _knn_bundle
    if _knn_bundle is not None:
        return _knn_bundle

    if os.path.exists(MODEL_PATH):
        logger.info(f"Memuat model KNN dari: {MODEL_PATH}")
        _knn_bundle = joblib.load(MODEL_PATH)
    else:
        logger.warning(f"File {MODEL_PATH} tidak ditemukan, melatih model KNN otomatis...")
        from train_model import train_knn
        if not os.path.exists(OUTFITS_CSV_PATH):
            from scripts.build_dataset import build_outfits_dataframe
            df = build_outfits_dataframe()
            os.makedirs(DATA_DIR, exist_ok=True)
            df.to_csv(OUTFITS_CSV_PATH, index=False)
        else:
            df = pd.read_csv(OUTFITS_CSV_PATH)

        _knn_bundle = train_knn(df)
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(_knn_bundle, MODEL_PATH)

    return _knn_bundle


def find_combinations(
    lab: Union[Tuple[float, float, float], List[float]],
    k: int = 10
) -> List[Dict[str, Any]]:
    """Mencari k paduan outfit serasi terdekat berdasarkan koordinat ruang warna CIELAB.
    
    Args:
        lab: [L, a, b] dari warna terdeteksi.
        k: Jumlah tetangga terdekat yang diambil dari dataset outfits.
        
    Returns:
        List[Dict[str, Any]]: Daftar kombinasi pakaian terdekat dengan jarak Euclidean CIELAB.
    """
    if len(lab) != 3:
        raise ValueError("Input CIELAB harus memiliki 3 elemen: [L, a, b]")

    bundle = load_knn_model()
    model = bundle["model"]
    records = bundle["outfits_records"]

    total_records = len(records)
    actual_k = max(1, min(k, total_records))

    query_vector = np.array([[float(lab[0]), float(lab[1]), float(lab[2])]], dtype=np.float32)
    distances, indices = model.kneighbors(query_vector, n_neighbors=actual_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        item = records[idx]
        results.append({
            "combo_name": str(item["combo_name"]),
            "combo_hex": str(item["combo_hex"]).upper(),
            "distance": round(float(dist), 2),
            "base_name": str(item["base_name"]),
            "base_hex": str(item["base_hex"]).upper(),
        })

    return results
