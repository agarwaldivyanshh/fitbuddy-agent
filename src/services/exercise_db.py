cat > src/services/exercise_db.py <<'PY'
"""
Exercise Database Loader

Creates a small CSV (if it doesn't exist) containing sample exercises.
This acts as the knowledge base for RAG retrieval and the PlannerAgent.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EX_CSV = DATA_DIR / "exercises.csv"


def ensure_sample_exercises():
    """Create a small exercise CSV if not already present."""
    if not EX_CSV.exists():
        df = pd.DataFrame([
            {"name": "Push Ups", "type": "bodyweight", "muscle": "chest"},
            {"name": "Squats", "type": "bodyweight", "muscle": "legs"},
            {"name": "Dumbbell Rows", "type": "dumbbell", "muscle": "back"},
            {"name": "Plank", "type": "bodyweight", "muscle": "core"},
            {"name": "Lunges", "type": "bodyweight", "muscle": "legs"},
            {"name": "Shoulder Press", "type": "dumbbell", "muscle": "shoulders"},
        ])
        df.to_csv(EX_CSV, index=False)
    return EX_CSV


def load_exercises():
    """Loads exercise CSV into a DataFrame."""
    ensure_sample_exercises()
    return pd.read_csv(EX_CSV)
PY
