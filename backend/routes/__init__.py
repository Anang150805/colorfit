"""Inisialisasi Blueprint Routes ColorFit."""

from routes.classify import classify_bp
from routes.detect import detect_bp
from routes.analyze import analyze_bp

__all__ = ["classify_bp", "detect_bp", "analyze_bp"]
