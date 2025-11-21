"""
PDF Exporter

Uses reportlab to create a simple PDF containing:
- Grocery list
- Optionally workout plan summary (day 1 only for the starter)

This is enough to demonstrate tool integration for the capstone.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
import json

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_plan_to_pdf(plan: dict, filename: str = "fitbuddy_plan.pdf") -> Path:
    """
    Creates a simple PDF summarising grocery list and day 1 workout.
    Returns the path to the created PDF.
    """

    out_path = EXPORT_DIR / filename
    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter

    y = height - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "FitBuddy — Weekly Plan Summary")
    y -= 30

    # --- Grocery list ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Grocery List:")
    y -= 20

    c.setFont("Helvetica", 10)
    for item in plan.get("grocery_list", []):
        c.drawString(60, y, f"- {item}")
        y -= 14
        if y < 50:
            c.showPage()
            y = height - 40

    # --- Optional: Workout Day 1 ---
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Workout Plan (Day 1):")
    y -= 20
    c.setFont("Helvetica", 10)

    day1 = plan.get("workout_plan", {}).get("day_1", {})
    c.drawString(60, y, f"Type: {day1.get('type', 'N/A')}")
    y -= 20

    exercises = day1.get("exercises", [])
    for ex in exercises:
        line = f"- {ex['name']}  ({ex['sets']} sets x {ex['reps']} reps)"
        c.drawString(60, y, line)
        y -= 14
        if y < 50:
            c.showPage()
            y = height - 40

    c.save()
    return out_path


# Run small demo if executed
if __name__ == "__main__":
    sample_plan = {
        "grocery_list": ["Oats", "Paneer", "Chickpeas"],
        "workout_plan": {
            "day_1": {
                "type": "Upper Body",
                "exercises": [
                    {"name": "Push Ups", "sets": 3, "reps": 12},
                    {"name": "Dumbbell Rows", "sets": 3, "reps": 10},
                ]
            }
        }
    }
    print("Exporting sample PDF...")
    path = export_plan_to_pdf(sample_plan, "sample_plan.pdf")
    print("Created PDF at:", path)
