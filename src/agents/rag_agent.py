"""
rag_agent.py

RAGAgent: builds a small knowledge index from the local exercise + nutrition CSVs
and provides a simple retrieval interface for the PlannerAgent.

Usage:
    from src.agents.rag_agent import build_knowledge_and_index, retrieve
    vs = build_knowledge_and_index()
    hits = retrieve(vs, "high protein vegetarian", top_k=3)
"""

from pathlib import Path
from typing import List, Dict
from ..services.exercise_db import load_exercises
from ..services.nutrition_db import load_nutrition
from ..services.vectorstore import SimpleVectorStore

def _make_documents():
    """
    Create text documents (strings) and metadata entries from the local CSVs.
    Returns (texts: List[str], metas: List[dict])
    """
    texts: List[str] = []
    metas: List[Dict] = []

    ex_df = load_exercises()
    for _, r in ex_df.iterrows():
        text = f"{r['name']} - exercise - type:{r.get('type','')}, muscle:{r.get('muscle','')}"
        texts.append(text)
        metas.append({"type": "exercise", "name": r["name"], "source": "exercises.csv"})

    nut_df = load_nutrition()
    for _, r in nut_df.iterrows():
        # include protein/calories fields if present
        cal = r.get("calories", r.get("cal_per_100g", ""))
        prot = r.get("protein", r.get("protein_g", ""))
        text = f"{r['name']} - food - calories:{cal}, protein:{prot}g"
        texts.append(text)
        metas.append({"type": "food", "name": r["name"], "calories": cal, "protein": prot, "source": "nutrition.csv"})

    return texts, metas


def build_knowledge_and_index() -> SimpleVectorStore:
    """
    Build (or rebuild) the local vector index from CSVs.
    Returns the SimpleVectorStore instance.
    """
    texts, metas = _make_documents()
    vs = SimpleVectorStore()
    vs.index_texts(texts, metas)
    return vs


def retrieve(vs: SimpleVectorStore, query: str, top_k: int = 3):
    """
    Query the vectorstore and return metadata hits.
    Returns a list of metadata dicts (may be empty).
    """
    if vs is None:
        return []
    return vs.query(query, top_k=top_k)


# small CLI test if run directly
if __name__ == "__main__":
    print("Building RAG index...")
    vs = build_knowledge_and_index()
    print("Done. Sample queries:")
    for q in ["high protein vegetarian", "leg exercises", "core workout"]:
        hits = retrieve(vs, q, top_k=3)
        print(f"Query: {q} -> {hits}")
