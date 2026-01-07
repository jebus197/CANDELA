"""
guardian_runtime.py
Fast governance wrapper with:
• response cache
• async semantic detector (Mini-BERT)
Safe: standalone file, no edits needed elsewhere except import hook below.
"""
from __future__ import annotations
import hashlib, threading, time, yaml
from pathlib import Path
from typing import Dict, Tuple
from .guardian_extended import guardian as _guardian_fast
from .detectors.mini_semantic import semantic_block   # semantic detector

# ── config --------------------------------------------------------------
CFG = yaml.safe_load(Path("config/guardian_scoring.yaml").read_text("utf-8"))
MODE        = CFG.get("mode", "sync_light")
BUDGET_MS   = int(CFG.get("latency_budget_ms", 120))
CACHE_TTL   = int(CFG.get("cache_ttl_s", 86400))
THRESHOLD   = float(CFG.get("detectors", {}).get("mini_semantic", {}).get("threshold", 0.80))

DIRECTIVES_HASH  = "c2664a99eb7f98f46d368815184158cbd74b8572d61974663c45726f8235e9cd"
_cache: Dict[str, Tuple[float, dict]] = {}

# ── helpers -------------------------------------------------------------
def _sha(txt: str) -> str:
    return hashlib.sha256(txt.encode()).hexdigest()

def _key(txt: str) -> str:
    return f"{_sha(txt)}::{DIRECTIVES_HASH}"

def _get(k: str):
    hit = _cache.get(k)
    return hit[1] if hit and hit[0] > time.time() else None

def _set(k: str, res: dict):
    _cache[k] = (time.time() + CACHE_TTL, res)

# ── public API ----------------------------------------------------------
def guardian_chat(text: str) -> dict:
    k = _key(text)
    if cached := _get(k):
        return cached

    t0 = time.perf_counter()
    res = _guardian_fast(text)
    dt_ms = (time.perf_counter() - t0) * 1_000
    if dt_ms > BUDGET_MS:
        res.setdefault("notes", []).append(f"background_pending:{int(dt_ms)}ms")
    _set(k, res)

    if MODE == "sync_light":
        threading.Thread(target=_bg_heavy_check, args=(text, k, THRESHOLD), daemon=True).start()
    return res

# ── background hook -----------------------------------------------------
def _bg_heavy_check(text: str, key: str, thresh: float):
    if semantic_block(text, thresh):
        _set(key, {"passed": False, "notes": ["semantic_block"]})
