"""Training Script untuk Model Machine Learning ColorFit.

Revisi:
1. Decision Tree:
   - Fitur: undertone (one-hot 3 kolom), hue_sin, hue_cos, saturation, value (total 7 fitur).
   - Menggunakan fungsi bersama extract_decision_tree_features dari services.color_features.
   - max_depth dibatasi (6-8) agar tidak overfit dan mudah dijelaskan.
   - Evaluasi 5-fold cross validation.
   - Fungsi export_rules() yang mengekspor aturan pohon teks ke backend/reports/tree_rules.txt.
2. KNN:
   - Menggunakan sklearn.neighbors.NearestNeighbors (fitur CIELAB L, a, b dengan jarak Euclidean).
3. Logging standar Python (bukan print).
"""

import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import accuracy_score

from services.color_features import extract_decision_tree_features, DT_FEATURE_NAMES

# Konfigurasi Logging Standar
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("colorfit.train_model")

# ==============================================================================
# KONSTANTA DAN KONFIGURASI
# ==============================================================================
DEFAULT_K = 5
MAX_TREE_DEPTH = 7
RANDOM_STATE = 42
TEST_SIZE = 0.20

DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def export_rules(clf: DecisionTreeClassifier, feature_names: list, output_path: str):
    """Mengekspor struktur pohon keputusan Decision Tree sebagai teks ke file reports/tree_rules.txt."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rules_text = export_text(
        clf,
        feature_names=feature_names,
        show_weights=True
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== ATURAN POHON KEPUTUSAN DECISION TREE COLORFIT ===\n")
        f.write(f"Kedalaman Maksimum (max_depth): {clf.max_depth}\n")
        f.write(f"Jumlah Fitur: {len(feature_names)}\n\n")
        f.write(rules_text)
    logger.info(f"Aturan pohon keputusan berhasil diekspor ke: {output_path}")


def train_decision_tree(colors_df: pd.DataFrame) -> dict:
    """Melatih DecisionTreeClassifier menggunakan 7 fitur (one-hot undertone, hue_sin, hue_cos, s, v)."""
    df = colors_df.copy()

    # Ekstrak 7 fitur menggunakan fungsi bersama color_features.py
    feature_matrix = []
    for _, row in df.iterrows():
        feat = extract_decision_tree_features(
            undertone=str(row["undertone"]),
            h=float(row["hue"]),
            s=float(row["saturation"]),
            v=float(row["value"]),
        )
        feature_matrix.append(feat)

    X = np.array(feature_matrix, dtype=np.float32)
    y = df["label"].values

    # Stratified Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    clf = DecisionTreeClassifier(
        max_depth=MAX_TREE_DEPTH,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
    )

    # 5-Fold Stratified Cross Validation pada data latih
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring="accuracy")

    clf.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, clf.predict(X_train))
    test_acc = accuracy_score(y_test, clf.predict(X_test))

    logger.info(f"[Decision Tree] Sampel Latih: {len(X_train)}, Sampel Uji: {len(X_test)}")
    logger.info(f"[Decision Tree] 5-Fold CV Accuracy: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")
    logger.info(f"[Decision Tree] Akurasi Data Latih: {train_acc * 100:.2f}%")
    logger.info(f"[Decision Tree] Akurasi Data Uji  : {test_acc * 100:.2f}%")

    # Ekspor aturan teks
    rules_path = os.path.join(REPORTS_DIR, "tree_rules.txt")
    export_rules(clf, DT_FEATURE_NAMES, rules_path)

    bundle = {
        "model": clf,
        "features": DT_FEATURE_NAMES,
        "classes": list(clf.classes_),
        "train_accuracy": float(train_acc),
        "test_accuracy": float(test_acc),
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
    }
    return bundle


def train_knn(outfits_df: pd.DataFrame) -> dict:
    """Melatih NearestNeighbors pada fitur CIELAB L, a, b outfits.csv."""
    df = outfits_df.copy()
    features = ["base_L", "base_a", "base_b"]
    X = df[features].values.astype(np.float32)

    # Fit NearestNeighbors dengan metrik Euclidean
    knn = NearestNeighbors(
        n_neighbors=DEFAULT_K,
        metric="euclidean",
        algorithm="auto"
    )
    knn.fit(X)

    logger.info(f"[KNN] Terlatih pada {len(df)} pasangan outfit serasi dengan K={DEFAULT_K}")

    bundle = {
        "model": knn,
        "outfits_records": df.to_dict(orient="records"),
        "features": features,
        "default_k": DEFAULT_K,
    }
    return bundle


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    colors_path = os.path.join(DATA_DIR, "colors.csv")
    outfits_path = os.path.join(DATA_DIR, "outfits.csv")

    if not os.path.exists(colors_path) or not os.path.exists(outfits_path):
        from scripts.build_dataset import main as build_data
        logger.info("Dataset belum lengkap, membangkitkan data/colors.csv dan outfits.csv...")
        build_data()

    colors_df = pd.read_csv(colors_path)
    outfits_df = pd.read_csv(outfits_path)

    logger.info("=== MEMULAI PELATIHAN MODEL MACHINE LEARNING COLORFIT ===")

    # 1. Latih Decision Tree
    dt_bundle = train_decision_tree(colors_df)
    dt_path = os.path.join(MODELS_DIR, "decision_tree.pkl")
    joblib.dump(dt_bundle, dt_path)
    logger.info(f"Model Decision Tree tersimpan ke: {dt_path}")

    # 2. Latih KNN NearestNeighbors
    knn_bundle = train_knn(outfits_df)
    knn_path = os.path.join(MODELS_DIR, "knn.pkl")
    joblib.dump(knn_bundle, knn_path)
    logger.info(f"Model KNN tersimpan ke: {knn_path}")


if __name__ == "__main__":
    main()
