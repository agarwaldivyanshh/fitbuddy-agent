"""
TrackerAgent

Simple progress logger + adaptation logic for FitBuddy.

Responsibilities:
- Log daily progress entries (date, completed_workouts, weight_kg, notes)
- Load past logs
- Compute a tiny adaptation decision based on recent performance

Storage:
- Saves progress to src/data/progress_log.json
"""

import json
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = DATA_DIR / "progress_log.json"


def _read_logs() -> List[Dict]:
    if LOG_PATH.exists():
        try:
            return json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _write_logs(logs: List[Dict]):
    LOG_PATH.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding="utf-8")


def log_progress_entry(entry: Dict):
    """
    entry example:
    {
      "date": "2025-11-20",
      "completed_workouts": 1,   # integer count for the day
      "weight_kg": 70.2,        # optional
      "notes": "Felt strong"
    }
    """
    logs = _read_logs()
    # normalize date if needed
    if "date" not in entry:
        entry["date"] = date.today().isoformat()
    logs.append(entry)
    _write_logs(logs)
    print(f"Saved progress entry for {entry['date']}")


def load_progress() -> List[Dict]:
    """Return list of logged entries (may be empty)."""
    return _read_logs()


def recent_summary(n_days: int = 14) -> Dict:
    """
    Compute a tiny summary over the last n_days:
    - total_workouts (sum completed_workouts)
    - avg_weight (if available)
    - days_logged
    """
    logs = _read_logs()
    if not logs:
        return {"total_workouts": 0, "avg_weight": None, "days_logged": 0}

    # filter last n_days (by date string)
    today = date.today()
    filtered = []
    for e in logs:
        try:
            d = datetime.fromisoformat(e["date"]).date()
        except Exception:
            continue
        if (today - d).days <= n_days:
            filtered.append(e)

    total_workouts = sum(e.get("completed_workouts", 0) for e in filtered)
    weights = [e.get("weight_kg") for e in filtered if e.get("weight_kg") is not None]
    avg_weight = sum(weights) / len(weights) if weights else None
    return {"total_workouts": total_workouts, "avg_weight": avg_weight, "days_logged": len(filtered)}


def adapt_plan_decision(recent_n_days: int = 14) -> Dict:
    """
    Tiny rule-based decision:
    - If user did >= (available_days * 2) workouts in recent_n_days -> suggest increase intensity
    - If user did <= (available_days) workouts in recent_n_days -> suggest reduce/maintain
    - Else maintain
    This function expects the intake profile to be available in data/profile.json
    """
    profile_path = DATA_DIR / "profile.json"
    profile = None
    if profile_path.exists():
        try:
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
        except Exception:
            profile = None

    available_days = int(profile.get("available_days", 4)) if profile else 4
    summary = recent_summary(n_days=recent_n_days)
    total_workouts = summary["total_workouts"]

    # thresholds
    two_weeks_target = available_days * 2  # expectation: complete roughly 2 * available_days over 14 days

    if total_workouts >= two_weeks_target + 2:
        decision = {"action": "increase_intensity", "reason": f"Completed {total_workouts} workouts in last {recent_n_days} days."}
    elif total_workouts <= max(0, available_days - 1):
        decision = {"action": "reduce_intensity_or_maintain", "reason": f"Only {total_workouts} workouts in last {recent_n_days} days."}
    else:
        decision = {"action": "maintain", "reason": f"{total_workouts} workouts in last {recent_n_days} days."}

    # include summary for display
    decision["summary"] = summary
    return decision


# Small CLI test
if __name__ == "__main__":
    print("TrackerAgent quick demo")
    log_progress_entry({"date": date.today().isoformat(), "completed_workouts": 1, "weight_kg": None, "notes": "Demo entry"})
    print("Recent summary:", recent_summary())
    print("Adapt decision:", adapt_plan_decision())
