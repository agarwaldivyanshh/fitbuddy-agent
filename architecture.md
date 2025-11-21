# FitBuddy Architecture

FitBuddy is designed as a small multi-agent system that generates a weekly workout plan, meal plan, and grocery list. It uses retrieval-augmented generation (RAG) to ground suggestions using a local database of exercises and foods.

## Agents

### 1. IntakeAgent
Collects:
- height, weight, age  
- fitness goal  
- dietary preferences (Indian-friendly)  
- available days  
- allergies  
- equipment available  

Stores this profile for all other agents.

---

### 2. RAGAgent
- Loads small CSV databases (nutrition and exercise)
- Uses embeddings + FAISS vector search to retrieve relevant items  
- Helps PlannerAgent choose realistic foods/exercises  

---

### 3. PlannerAgent
Uses:
- User profile  
- RAG results  
- Templates  

Produces:
- 7-day workout plan  
- 7-day meal plan  
- Grocery list  

Also exports the plan to JSON/PDF.

---

### 4. TrackerAgent
Tracks:
- daily workout completion  
- weight changes  
- protein consistency  
- energy/mood  
- Adapts next week's plan using simple logic  

---

## Data Sources
Local CSV files:
- `nutrition.csv`
- `exercises.csv`

Vector store:
- FAISS index + sentence-transformers embeddings

---

## High-level flow

User → IntakeAgent → RAGAgent → PlannerAgent → Export  
                  ↘ TrackerAgent (adapts future plans)

---

See `arch_diagram.mmd` for the diagram code.
