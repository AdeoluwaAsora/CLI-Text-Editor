import numpy as np
from typing import List, Tuple
from .embed import BagOfWords

class SimpleIndex:
    def __init__(self, dim: int = 512):
        self.embedder = BagOfWords(dim)
        self.texts: List[str] = []
        self.vecs: np.ndarray | None = None

    def add(self, docs: List[str]):
        if not docs: return
        enc = self.embedder.encode(docs)  # L2-normalized
        self.texts.extend(docs)
        self.vecs = enc if self.vecs is None else np.vstack([self.vecs, enc])

    def search(self, query: str, k: int = 5) -> List[Tuple[int, float, str]]:
        if self.vecs is None or not len(self.texts):
            return []
        q = self.embedder.encode([query])  # L2-normalized
        sims = (self.vecs @ q.T).ravel()   # cosine since normalized
        idx = np.argsort(-sims)[:k]
        return [(int(i), float(sims[i]), self.texts[i]) for i in idx]
