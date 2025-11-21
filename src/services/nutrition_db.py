"""
Nutrition Database Loader

Creates a small CSV (if missing) with Indian-friendly foods and their
approx calories & protein. Used by RAG and PlannerAgent.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

NUT_CSV = DATA_DIR / "nutrition.csv"


def ensure_sample_nutrition():
    """Create a simple nutrition CSV if missing."""
    if not NUT_CSV.exists():
        df = pd.DataFrame([
            {"name": "Oats", "calories": 389, "protein": 13.5},
            {"name": "Paneer", "calories": 265, "protein": 18},
            {"name": "Dal", "calories": 116, "protein": 9},
            {"name": "Chickpeas", "calories": 164, "protein": 9},
            {"name": "Banana", "calories": 89, "protein": 1.1},
            {"name": "Peanut Butter", "calories": 588, "protein": 25},
            {"name": "Brown Rice", "calories": 123, "protein": 2.7},
            {"name": "Curd", "calories": 98, "protein": 11},
        ])
        df.to_csv(NUT_CSV, index=False)
    return NUT_CSV


def load_nutrition():
    """Loads nutrition CSV into a DataFrame."""
    ensure_sample_nutrition()
    return pd.read_csv(NUT_CSV)
