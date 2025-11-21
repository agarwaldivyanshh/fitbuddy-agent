"""
Streamlit UI for FitBuddy (simple demo)

Run locally (optional):
    streamlit run src/app.py

This minimal UI:
- Lets the user save a profile
- Builds the RAG index (if not present)
- Generates a 7-day plan using PlannerAgent
- Shows Day 1 workout & grocery list
- Exports a PDF and provides the file path

Note: This UI keeps everything file-based and dependency-light so judges can run it easily.
"""

import streamlit as st
import json
from pathlib import Path

# local agents/services
from agents.intake_agent import load_profile, save_profile, default_profile
from agents.rag_agent import build_knowledge_and_index, retrieve
from agents.planner_agent import plan_from_profile
from services.pdf_exporter import export_plan_to_pdf

# small utility to read last plan
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
LAST_PLAN = DATA_DIR / "last_plan.json"

st.set_page_config(page_title="FitBuddy Demo", layout="wide")

st.title("FitBuddy — Gym & Meal Planner (Demo)")

# Sidebar: profile editor
st.sidebar.header("Profile")
profile = load_profile() or default_profile()

name = st.sidebar.text_input("Name", value=profile.get("name", "Student"))
age = st.sidebar.number_input("Age", min_value=12, max_value=80, value=int(profile.get("age", 20)))
height = st.sidebar.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=float(profile.get("height_cm", 170.0)))
weight = st.sidebar.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=float(profile.get("weight_kg", 65.0)))
goal = st.sidebar.selectbox("Goal", options=["lose", "gain", "maintain"], index=0)
activity = st.sidebar.selectbox("Activity level", options=["sedentary", "moderate", "active"], index=1)
diet = st.sidebar.text_input("Diet (e.g. vegetarian)", value=profile.get("diet", "vegetarian"))
available_days = st.sidebar.slider("Available days/week", min_value=1, max_value=7, value=int(profile.get("available_days", 4)))
equipment = st.sidebar.text_input("Equipment (comma-separated)", value=",".join(profile.get("equipment", ["none"])))

if st.sidebar.button("Save profile"):
    new_profile = {
        "name": name, "age": int(age), "sex": profile.get("sex", "M"),
        "height_cm": float(height), "weight_kg": float(weight),
        "goal": goal, "activity_level": activity, "diet": diet,
        "available_days": int(available_days),
        "equipment": [e.strip() for e in equipment.split(",") if e.strip()]
    }
    save_profile(new_profile)
    st.sidebar.success("Profile saved")

st.markdown("---")

# Main area: generate plan
st.header("Generate Plan")
st.write("Click **Generate Plan** to build a 7-day workout + meal plan and grocery list.")

if st.button("Generate Plan"):
    profile = load_profile()
    if not profile:
        st.error("Save a profile in the sidebar first.")
    else:
        with st.spinner("Building knowledge index (one-time) and generating plan..."):
            vs = build_knowledge_and_index()
            rag_hits = retrieve(vs, "high protein vegetarian", top_k=4)
            plan = plan_from_profile(profile, rag_results=rag_hits)

            # show a quick summary
            st.subheader("Workout — Day 1")
            day1 = plan["workout_plan"]["day_1"]
            if day1.get("type") == "Rest":
                st.write("Rest day")
            else:
                st.write(f"Type: {day1.get('type')}")
                st.table(day1.get("exercises"))

            st.subheader("Grocery List (sample)")
            st.write(plan.get("grocery_list"))

            # save last plan preview
            with open(LAST_PLAN, "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)

            # export PDF
            pdf_path = export_plan_to_pdf(plan, filename=f"fitbuddy_plan_{profile.get('name','user')}.pdf")
            st.success(f"Plan generated and exported to: {pdf_path}")
            st.write("You can download the file from the repository `src/data/exports/` after running locally.")
            st.write("If you deploy to Streamlit Cloud, you can wire the file for download or show a link.")

# Option: show last plan if exists
st.markdown("---")
if LAST_PLAN.exists():
    try:
        with open(LAST_PLAN, "r", encoding="utf-8") as f:
            last = json.load(f)
        st.header("Last Generated Plan Preview")
        st.write("Grocery List:", last.get("grocery_list"))
        st.write("Day 1 workout:", last.get("workout_plan", {}).get("day_1"))
    except Exception:
        st.write("No preview available.")
