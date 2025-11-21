"""
IntakeAgent

Collects and persists a simple user profile for FitBuddy.
This module is intentionally beginner-friendly and dependency-free.

How to use:
- From CLI: `python src/agents/intake_agent.py`
- From other code: `from src.agents.intake_agent import load_profile, save_profile, collect_profile_interactive`

Data is stored in `src/data/profile.json`.
"""

import json
from pathlib import Path
from datetime import datetime

# Data folder (relative to project root)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_PATH = DATA_DIR / "profile.json"


def default_profile():
    """Return a small default profile template."""
    return {
        "name": "Student",
        "age": 20,
        "sex": "M",
        "height_cm": 170.0,
        "weight_kg": 65.0,
        "goal": "maintain",            # options: lose / gain / maintain
        "activity_level": "moderate",  # sedentary / moderate / active
        "diet": "vegetarian",          # e.g. vegetarian, non-veg, ovo-veg
        "allergies": [],               # e.g. ["peanut"]
        "equipment": ["none"],         # e.g. ["dumbbells", "barbell"]
        "available_days": 4,           # days per week user can train
        "created_at": None,
        "last_updated": None
    }


def save_profile(profile: dict):
    """Persist profile to disk (PROFILE_PATH). Adds timestamps."""
    profile = dict(profile)  # shallow copy
    now = datetime.utcnow().isoformat()
    if profile.get("created_at") is None:
        profile["created_at"] = now
    profile["last_updated"] = now

    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    return PROFILE_PATH


def load_profile() -> dict | None:
    """Load profile from disk. Returns None if not present."""
    if PROFILE_PATH.exists():
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def collect_profile_interactive() -> dict:
    """Interactively collect profile details from the user (CLI)."""
    print("=== FitBuddy Intake (interactive) ===")
    p = load_profile() or default_profile()

    def ask(key, cast=str, prompt=None, default=None):
        prompt = prompt or f"{key} ({default}): "
        raw = input(prompt).strip()
        if raw == "":
            return default
        try:
            return cast(raw)
        except Exception:
            print(f"Couldn't parse input; keeping default: {default}")
            return default

    # Ask basic details. We show current/default values for convenience.
    p["name"] = ask("Name", str, f"Name [{p['name']}] ", p["name"])
    p["age"] = ask("Age", int, f"Age [{p['age']}] ", p["age"])
    p["sex"] = ask("Sex (M/F)", str, f"Sex [{p['sex']}] ", p["sex"])
    p["height_cm"] = ask("Height (cm)", float, f"Height_cm [{p['height_cm']}] ", p["height_cm"])
    p["weight_kg"] = ask("Weight (kg)", float, f"Weight_kg [{p['weight_kg']}] ", p["weight_kg"])
    p["goal"] = ask("Goal (lose/gain/maintain)", str, f"Goal [{p['goal']}] ", p["goal"])
    p["activity_level"] = ask("Activity (sedentary/moderate/active)", str,
                              f"Activity_level [{p['activity_level']}] ", p["activity_level"])
    diet = ask("Dietary prefs (comma-separated, e.g. vegetarian,no-eggs)", str,
               f"Diet [{p['diet']}] ", p["diet"])
    # normalize diet to single string (keep simple)
    p["diet"] = diet if isinstance(diet, str) else p["diet"]

    allergies = ask("Allergies (comma-separated, leave blank if none)", str, "Allergies [] ", "")
    p["allergies"] = [a.strip() for a in allergies.split(",") if a.strip()] if allergies else p["allergies"]

    equipment = ask("Equipment (comma-separated, e.g. dumbbells,none)", str,
                    "Equipment [none] ", ",".join(p["equipment"]))
    p["equipment"] = [e.strip() for e in equipment.split(",") if e.strip()]

    p["available_days"] = ask("Available days/week (1-7)", int,
                              f"Available_days [{p['available_days']}] ", p["available_days"])

    # Save & show quick summary
    save_path = save_profile(p)
    print(f"\nProfile saved to: {save_path}")
    print("Summary:")
    for k, v in p.items():
        if k in ("created_at", "last_updated"):
            continue
        print(f" - {k}: {v}")
    return p


if __name__ == "__main__":
    # If run directly, interactively collect and save profile.
    collect_profile_interactive()
