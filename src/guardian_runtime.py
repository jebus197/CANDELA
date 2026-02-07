"""
guardian_runtime.py
Fast governance wrapper with:
• response cache
• async semantic detector (MiniLM / all-MiniLM-L6-v2)
Safe: standalone file, no edits needed elsewhere except import hook below.
"""
from __future__ import annotations
import hashlib, json, threading, time, yaml
from pathlib import Path
from typing import Dict, Tuple
from .guardian_extended import guardian as _guardian_fast
from .detectors.mini_semantic import semantic_block   # semantic detector
from concurrent.futures import ThreadPoolExecutor
from .directive_validation import validate_output as _validate_directives

# ── config --------------------------------------------------------------
CFG = yaml.safe_load(Path("config/guardian_scoring.yaml").read_text("utf-8"))
MODE        = CFG.get("mode", "strict")  # strict | sync_light | regex_only
BUDGET_MS   = int(CFG.get("latency_budget_ms", 120))
CACHE_TTL   = int(CFG.get("cache_ttl_s", 86400))
THRESHOLD   = float(CFG.get("detectors", {}).get("mini_semantic", {}).get("threshold", 0.80))
SEM_ENABLED = bool(CFG.get("detectors", {}).get("mini_semantic", {}).get("enabled", True))

VAL_CFG = CFG.get("validation", {}) or {}
ENFORCE_CONFIDENCE = bool(VAL_CFG.get("enforce_confidence_tag", False))
ENFORCE_UNCERTAIN = bool(VAL_CFG.get("enforce_uncertain_tag", False))
ENFORCE_MICROFORMATS = bool(VAL_CFG.get("enforce_microformats", True))

DIRECTIVES_HASH  = "7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d"
_cache: Dict[str, Tuple[float, dict]] = {}
LOG_DIR   = Path("logs")
LOG_FILE  = LOG_DIR / "output_log.jsonl"
LAT_FILE  = LOG_DIR / "latency_log.jsonl"
_PRELOAD_DONE = False
_EXECUTOR = ThreadPoolExecutor(max_workers=1)

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

def _log_latency(mode: str, dt_fast_ms: float, dt_sem_ms: float | None, cached: bool):
    LAT_FILE.parent.mkdir(exist_ok=True)
    entry = {
        "ts": time.time(),
        "mode": mode,
        "cached": cached,
        "dt_fast_ms": round(dt_fast_ms, 3),
        "dt_sem_ms": round(dt_sem_ms, 3) if dt_sem_ms is not None else None,
    }
    LAT_FILE.open("a", encoding="utf-8").write(json.dumps(entry) + "\n")

def _log_output(text: str, res: dict):
    """Append the checked text + verdict to an append-only log for Merkle anchoring."""
    LOG_DIR.mkdir(exist_ok=True)
    entry = {
        "ts": time.time(),
        "directive_hash": DIRECTIVES_HASH,
        "text_sha256": _sha(text),
        "text": text,
        "verdict": res,
    }
    LOG_FILE.open("a", encoding="utf-8").write(json.dumps(entry, ensure_ascii=False) + "\n")

def _warm_semantic():
    global _PRELOAD_DONE
    if _PRELOAD_DONE:
        return
    try:
        # One dummy call to load model weights and allocations
        if SEM_ENABLED:
            semantic_block("warmup", THRESHOLD)
        _PRELOAD_DONE = True
    except Exception:
        # Do not block startup if warmup fails
        pass

# ── public API ----------------------------------------------------------
def guardian_chat(text: str) -> dict:
    _EXECUTOR.submit(_warm_semantic)
    k = _key(text)
    if cached := _get(k):
        _log_latency(MODE, 0.0, None, cached=True)
        return cached

    t0 = time.perf_counter()
    res = _guardian_fast(text)
    dt_fast = (time.perf_counter() - t0) * 1_000

    # strict mode blocks on semantic; sync_light returns quickly and may update later.
    dt_sem = None
    if MODE == "strict" and SEM_ENABLED and res.get("passed", True):
        t1 = time.perf_counter()
        if semantic_block(text, THRESHOLD):
            res = {"passed": False, "notes": ["semantic_block"], "violations": ["semantic_block"], "score": 0}
        dt_sem = (time.perf_counter() - t1) * 1_000
    elif MODE == "sync_light" and SEM_ENABLED and res.get("passed", True):
        threading.Thread(target=_bg_heavy_check, args=(text, k, THRESHOLD), daemon=True).start()
        if dt_fast > BUDGET_MS:
            res.setdefault("notes", []).append(f"background_pending:{int(dt_fast)}ms")

    # Directive-criteria validations (structure-triggered to reduce false positives)
    findings = _validate_directives(
        text,
        enforce_confidence_tag=ENFORCE_CONFIDENCE,
        enforce_uncertain_tag=ENFORCE_UNCERTAIN,
        enforce_microformats=ENFORCE_MICROFORMATS,
    )
    for f in findings:
        if f.level == "violation":
            res.setdefault("violations", []).append(f"directive_{f.key}")
            res["passed"] = False
            res.setdefault("score", 0)
        else:
            res.setdefault("notes", []).append(f"{f.key}:{f.message}")

    _set(k, res)
    _log_output(text, res)
    _log_latency(MODE, dt_fast, dt_sem, cached=False)
    return res

# ── background hook -----------------------------------------------------
def _bg_heavy_check(text: str, key: str, thresh: float):
    if semantic_block(text, thresh):
        _set(key, {"passed": False, "notes": ["semantic_block"]})
        _log_output(text, {"passed": False, "notes": ["semantic_block"]})
