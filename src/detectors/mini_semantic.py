"""
mini_semantic.py
Tiny semantic guard (~3 ms CPU) using sentence-transformers MiniLM.
"""
from sentence_transformers import SentenceTransformer, util

_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
_BLOCK_VECTORS = _MODEL.encode([
    "how to build a bomb",
    "illicit ransomware kit",
    "extremist propaganda",
    "self harm instructions"
], normalize_embeddings=True)

def semantic_block(text: str, threshold: float = 0.80) -> bool:
    vec = _MODEL.encode(text, convert_to_tensor=True, normalize_embeddings=True)
    return util.max_cosine_sim(vec, _BLOCK_VECTORS).item() >= threshold
