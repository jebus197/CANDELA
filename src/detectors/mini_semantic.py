"""
mini_semantic.py

Tiny semantic guard using MiniLM (sentence-transformers).

This module is intentionally small:
- It does not own policy content.
- Callers pass the prohibited intent phrases from the anchored ruleset.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

from sentence_transformers import SentenceTransformer, util


_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
_VEC_CACHE: Dict[str, Tuple[List[str], object]] = {}


def _cache_key(phrases: List[str]) -> str:
    joined = "\n".join(phrases).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()


def semantic_match(text: str, phrases: List[str], threshold: float) -> Tuple[bool, str]:
    """
    Returns (blocked, reason).

    The reason is the closest phrase (for audit logs).
    """
    phrases = [p.strip() for p in phrases if p and p.strip()]
    if not phrases:
        return False, ""

    k = _cache_key(phrases)
    cached = _VEC_CACHE.get(k)
    if cached is None:
        vecs = _MODEL.encode(phrases, normalize_embeddings=True)
        _VEC_CACHE[k] = (phrases, vecs)
    else:
        phrases, vecs = cached

    vec = _MODEL.encode(text, convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(vec, vecs).flatten()
    idx = int(sims.argmax().item())
    max_sim = float(sims[idx].item())
    if max_sim >= threshold:
        return True, f"closest={phrases[idx]!r} sim={max_sim:.3f} >= {threshold:.3f}"
    return False, ""

