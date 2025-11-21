"""
Simple vectorstore wrapper.

Behavior:
- Tries to use `faiss` + `sentence-transformers` for fast, persistent indexing.
- If faiss is not available, falls back to sklearn's NearestNeighbors (in-memory).
- Keeps a small metadata list so queries return the original items.

Usage:
from src.services.vectorstore import SimpleVectorStore
vs = SimpleVectorStore()
vs.index_texts(["Push Ups - chest", "Squats - legs"], [{"name":"Push Ups"},{"name":"Squats"}])
hits = vs.query("chest exercise", top_k=2)
"""

from pathlib import Path
import pickle
import numpy as np

# try imports
try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False

from sentence_transformers import SentenceTransformer

# fallback imports
if not FAISS_AVAILABLE:
    from sklearn.neighbors import NearestNeighbors

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
IDX_PATH = DATA_DIR / "faiss.index"
META_PATH = DATA_DIR / "vs_metadata.pkl"

# choose a compact embedding model
_EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


class SimpleVectorStore:
    def __init__(self):
        self.model = SentenceTransformer(_EMBED_MODEL_NAME)
        self.metadata = []
        self.embeddings = None  # used by sklearn fallback
        self.index = None
        # load existing index/metadata if present (faiss mode)
        if FAISS_AVAILABLE and IDX_PATH.exists() and META_PATH.exists():
            try:
                self.index = faiss.read_index(str(IDX_PATH))
                self.metadata = pickle.load(open(META_PATH, "rb"))
            except Exception:
                # If loading fails, we'll rebuild when indexing
                self.index = None
                self.metadata = []

        # sklearn fallback will build index when needed
        if not FAISS_AVAILABLE and META_PATH.exists():
            try:
                data = pickle.load(open(META_PATH, "rb"))
                self.metadata = data.get("metadata", [])
                self.embeddings = data.get("embeddings", None)
                if self.embeddings is not None:
                    self._build_sklearn_index()
            except Exception:
                self.metadata = []
                self.embeddings = None

    def index_texts(self, texts: list[str], metadatas: list[dict]):
        """
        Index given texts (list of strings) with corresponding metadata list.
        Overwrites previous index.
        """
        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must be same length")

        embs = self.model.encode(texts, convert_to_numpy=True)
        self.metadata = metadatas

        if FAISS_AVAILABLE:
            d = embs.shape[1]
            self.index = faiss.IndexFlatL2(d)
            self.index.add(embs)
            # persist
            faiss.write_index(self.index, str(IDX_PATH))
            pickle.dump(self.metadata, open(META_PATH, "wb"))
        else:
            # sklearn fallback: store embeddings and build nearest neighbors index
            self.embeddings = embs
            self._build_sklearn_index()
            # persist metadata + embeddings
            pickle.dump({"metadata": self.metadata, "embeddings": self.embeddings}, open(META_PATH, "wb"))

    def _build_sklearn_index(self):
        if self.embeddings is None:
            return
        self.index = NearestNeighbors(n_neighbors=min(10, len(self.embeddings)), metric="cosine")
        self.index.fit(self.embeddings)

    def query(self, text: str, top_k: int = 3) -> list[dict]:
        """
        Returns a list of metadata dicts (length up to top_k) most similar to `text`.
        """
        if (self.index is None) and (not FAISS_AVAILABLE):
            return []

        q_emb = self.model.encode([text], convert_to_numpy=True)

        if FAISS_AVAILABLE and self.index is not None:
            # search faiss
            D, I = self.index.search(q_emb, top_k)
            results = []
            for idx in I[0]:
                if idx < len(self.metadata):
                    results.append(self.metadata[idx])
            return results

        # sklearn fallback
        if not FAISS_AVAILABLE and self.index is not None:
            distances, indices = self.index.kneighbors(q_emb, n_neighbors=min(top_k, len(self.metadata)))
            results = []
            for idx in indices[0]:
                if idx < len(self.metadata):
                    results.append(self.metadata[idx])
            return results

        return []
