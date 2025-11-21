# FitBuddy — AI Gym & Meal Planner Agent

**Track:** Concierge Agents  
**Short pitch:** FitBuddy generates personalized weekly workout plans, budget-friendly Indian-style meal plans, and grocery lists; it adapts using user progress and uses retrieval-augmented generation (RAG) to ground recommendations.

---

## Project Status
Starter implementation + prompt templates + Streamlit demo scaffold. This repo is structured to demonstrate the multi-agent architecture, RAG, memory, and export features required by the capstone evaluation.

---

## Why this project (Problem)
Many students and busy professionals struggle to get practical, affordable fitness and meal plans tailored to their constraints (budget, dietary preferences, equipment, time). Public fitness advice is generic and hard to follow. A concierge agent can orchestrate intake, planning, tracking, and reminders — and adapt plans over time.

## Solution
FitBuddy is a multi-agent system:
- **IntakeAgent**: collects user info (body stats, schedule, preferences)  
- **PlannerAgent**: builds a 7-day workout + meal plan and grocery list  
- **RAGAgent**: grounds suggestions using a nutrition & exercise knowledge base  
- **TrackerAgent**: stores progress and adapts future plans

Key features implemented:
- Multi-agent orchestration (Intake → Planner → Tracker)  
- Retrieval-Augmented Generation (RAG) using a small CSV-backed vector store  
- Memory (persistent user profiles and progress)  
- Export to JSON / PDF (grocery list + plan)  
- Streamlit UI for demo (single-file app)

---

## How this maps to evaluation rubric
- **Pitch (30 pts)**: Problem + solution + value documented in this README and arch diagram.  
- **Implementation (50 pts)**: Multi-agent orchestration, RAG, memory, tool integration demonstrated in `src/`.  
- **Documentation (20 pts)**: README, architecture.md, inline code comments, demo screenshots.  
- **Bonus**: Designed to integrate with Gemini (prompt templates included) and deploy on Streamlit Cloud or Cloud Run.

---

## Quickstart (local)

1. Clone:
```bash
git clone https://github.com/<your-username>/fitbuddy-agent.git
cd fitbuddy-agent
