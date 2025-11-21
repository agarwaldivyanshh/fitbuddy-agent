import json
from pathlib import Path
from src.agents.planner_agent import plan_from_profile
from src.agents.intake_agent import default_profile

def test_plan_contains_expected_keys():
    """
    Ensure plan_from_profile returns the expected structure.
    """
    p = default_profile()
    p["available_days"] = 4
    p["goal"] = "maintain"
    p["diet"] = "vegetarian"
    p["equipment"] = ["none"]

    plan = plan_from_profile(p, rag_results=None)

    assert isinstance(plan, dict)
    assert "workout_plan" in plan
    assert "meal_plan" in plan
    assert "grocery_list" in plan
    # workout_plan should have 7 keys (day_1 ... day_7)
    assert len(plan["workout_plan"]) == 7
    # each day has a type
    assert "type" in plan["workout_plan"]["day_1"]
