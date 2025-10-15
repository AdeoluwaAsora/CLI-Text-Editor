import numpy as np
from typing import Iterable

class BagOfWords:
    """Tiny, dependency-free embedder: hashed bag-of-words + L2 normalize."""
    def __init__(self, dim: int = 512):
        self.dim = dim

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        vecs = []
        for t in texts:
            v = np.zeros(self.dim, dtype=np.float32)
            for tok in t.lower().split():
                v[hash(tok) % self.dim] += 1.0
            n = np.linalg.norm(v) or 1.0
            vecs.append(v / n)
        return np.vstack(vecs)
