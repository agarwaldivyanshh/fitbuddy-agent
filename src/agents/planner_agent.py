"""
PlannerAgent

Generates a simple 7-day workout plan, meal plan and grocery list using:
- the user's profile
- local nutrition & exercise databases
- optional RAG hits (metadata) from rag_agent

This is intentionally heuristic (no external LLM calls) so it's easy to run offline.
Later you can replace parts with prompt-based LLM generation (Gemini) for bonus points.
"""

import json
from pathlib import Path
from random import choice, sample, seed
from typing import Optional

# Use the same data folder used by other modules
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LAST_PLAN = DATA_DIR / "last_plan.json"

# local imports (these modules we added earlier)
from ..services.exercise_db import load_exercises
from ..services.nutrition_db import load_nutrition

# For reproducible sampling during tests/dev
seed(42)


def _choose_exercises_for_day(ex_df, equipment_list, day_type="Full Body", n=3):
    """
    Choose n exercises appropriate for the day's type and available equipment.
    This is a simple heuristic:
    - Prefer exercises matching muscles for the day (if possible)
    - Fallback to random selection
    """
    # map day_type to target muscles (simple)
    mapping = {
        "Full Body": ["chest", "legs", "back", "core", "shoulders"],
        "Upper Body": ["chest", "back", "shoulders"],
        "Lower Body": ["legs"],
        "Core": ["core"]
    }
    target_muscles = mapping.get(day_type, ["chest", "legs", "back"])

    # filter by equipment: if user has 'none', prefer bodyweight
    if equipment_list:
        equips = [e.lower() for e in equipment_list]
    else:
        equips = ["none"]

    # prefer exercises that match target muscles
    candidates = ex_df[ex_df['muscle'].isin(target_muscles)]
    if candidates.empty:
        candidates = ex_df

    # try to prefer bodyweight when no equipment
    if "none" in equips:
        bw = candidates[candidates['type'] == "bodyweight"]
        if len(bw) >= n:
            return bw['name'].sample(n).tolist()

    # otherwise random pick
    n = min(n, len(candidates))
    return candidates['name'].sample(n).tolist()


def _choose_meal_for_day(nut_df, diet="vegetarian"):
    """
    Pick one simple breakfast/lunch/dinner/snack from the nutrition DB.
    We try to keep meal items matching diet string if possible.
    Returns dict with meal items (names).
    """
    # simple diet filtering
    df = nut_df.copy()
    if diet and "veg" in diet.lower():
        # no guaranteed filtering available in the tiny DB, but attempt to avoid obvious non-veg names
        df = df[~df['name'].str.contains("Chicken|Fish|Egg", case=False, na=False)]
        if df.empty:
            df = nut_df.copy()

    # sample items (with replacement)
    breakfast = df.sample(1)['name'].tolist()
    lunch = df.sample(1)['name'].tolist()
    dinner = df.sample(1)['name'].tolist()
    snack = df.sample(1)['name'].tolist()

    return {
        "breakfast": breakfast[0],
        "lunch": lunch[0],
        "dinner": dinner[0],
        "snack": snack[0]
    }


def plan_from_profile(profile: dict,
                      rag_results: Optional[list] = None) -> dict:
    """
    Build a 7-day plan from profile.
    - profile: user profile dict (from intake_agent)
    - rag_results: optional list of metadata dicts returned by RAGAgent

    Returns:
    {
      "workout_plan": { "day_1": {...}, ... },
      "meal_plan": { "day_1": {...}, ... },
      "grocery_list": [...],
      "notes": "..."
    }
    """
    ex_df = load_exercises()
    nut_df = load_nutrition()

    # normalize profile entries
    available_days = int(profile.get("available_days", 4))
    equipment = profile.get("equipment", []) or []
    diet = profile.get("diet", "vegetarian")
    goal = profile.get("goal", "maintain")

    # Build workout split based on available_days
    # Simple mapping: fewer days -> full body; more days -> splits
    if available_days <= 3:
        splits = ["Full Body"] * 7
    elif available_days == 4:
        splits = ["Upper Body", "Lower Body", "Rest", "Upper Body", "Lower Body", "Core", "Rest"]
    else:
        # 5-7 days: rotate focus
        splits = ["Upper Body", "Lower Body", "Core", "Full Body", "Upper Body", "Lower Body", "Core"]

    # create plans
    workout_plan = {}
    meal_plan = {}
    grocery = set()

    for i in range(7):
        day_key = f"day_{i+1}"
        day_type = splits[i] if i < len(splits) else "Full Body"
        if day_type == "Rest":
            workout_plan[day_key] = {"type": "Rest", "exercises": []}
        else:
            exercises = _choose_exercises_for_day(ex_df, equipment, day_type=day_type, n=3)
            # simple sets/reps heuristic
            exercises_struct = []
            for ex in exercises:
                if goal == "gain":
                    sets, reps = 4, 8
                elif goal == "lose":
                    sets, reps = 3, 12
                else:
                    sets, reps = 3, 10
                exercises_struct.append({"name": ex, "sets": sets, "reps": reps})
            workout_plan[day_key] = {"type": day_type, "exercises": exercises_struct}

        # meal planning
        meals = _choose_meal_for_day(nut_df, diet=diet)
        meal_plan[day_key] = meals
        # add to grocery
        grocery.update([meals['breakfast'], meals['lunch'], meals['dinner'], meals['snack']])

    # Optionally incorporate RAG results: if rag_results contains high-protein foods, add them to grocery
    if rag_results:
        for hit in rag_results:
            if hit.get("type") == "food":
                grocery.add(hit.get("name"))

    out = {
        "workout_plan": workout_plan,
        "meal_plan": meal_plan,
        "grocery_list": sorted(list(grocery)),
        "notes": f"Generated for goal={goal}, available_days={available_days}, diet={diet}"
    }

    # persist last plan for tracker to use
    with open(LAST_PLAN, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    return out
