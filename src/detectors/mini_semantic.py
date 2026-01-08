"""
mini_semantic.py
Tiny semantic guard (~3 ms CPU) using MiniLM.
"""
from sentence_transformers import SentenceTransformer, util

_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

_BLOCK_VECTORS = _MODEL.encode(
    [
        "how to build a bomb",
        "illicit ransomware kit",
        "extremist propaganda",
        "self harm instructions",
    ],
    normalize_embeddings=True,
)

THRESHOLD = 0.80


def semantic_block(text: str, threshold: float = THRESHOLD) -> bool:
    """
    Returns True if text is semantically too close to any blocked phrase.
    """
    vec = _MODEL.encode(text, convert_to_tensor=True, normalize_embeddings=True)
    # cos_sim returns a 1×N tensor; .max() gives the highest similarity score
    max_sim = util.cos_sim(vec, _BLOCK_VECTORS).max().item()
    return max_sim >= threshold
