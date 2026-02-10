"""
guardian_runtime.py
Fast governance wrapper with:
• response cache
• async semantic detector (MiniLM / all-MiniLM-L6-v2)
Safe: standalone file, no edits needed elsewhere except import hook below.
"""
from __future__ import annotations
import hashlib, json, os, threading, time, yaml
from pathlib import Path
from typing import Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
from .directive_validation import canonical_ruleset_sha256, ruleset_path, validate_output as _validate_directives

# ── config --------------------------------------------------------------
CFG = yaml.safe_load(Path("config/guardian_scoring.yaml").read_text("utf-8"))
MODE        = CFG.get("mode", "strict")  # strict | sync_light | regex_only
BUDGET_MS   = int(CFG.get("latency_budget_ms", 120))
CACHE_TTL   = int(CFG.get("cache_ttl_s", 86400))
THRESHOLD   = float(CFG.get("detectors", {}).get("mini_semantic", {}).get("threshold", 0.80))
SEM_ENABLED = bool(CFG.get("detectors", {}).get("mini_semantic", {}).get("enabled", True))

LOG_CFG = CFG.get("logging", {}) or {}
LOG_STORE_TEXT = bool(LOG_CFG.get("store_text", True))
LOG_PREVIEW_CHARS = int(LOG_CFG.get("text_preview_chars", 0) or 0)

# Derived from the canonical JSON of the selected ruleset (default: src/directives_schema.json).
RULESET_PATH = ruleset_path()
DIRECTIVES_HASH = canonical_ruleset_sha256(RULESET_PATH)
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
    # Include semantic settings so cached results don't mix across modes/configs.
    return f"{_sha(txt)}::{DIRECTIVES_HASH}::{MODE}::{int(SEM_ENABLED)}::{THRESHOLD:.3f}"

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
    # Use a context manager to avoid file descriptor leaks under sustained runs.
    with LAT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def _log_output(text: str, res: dict):
    """Append the checked text + verdict to an append-only log for Merkle anchoring."""
    LOG_DIR.mkdir(exist_ok=True)
    entry = {
        "ts": time.time(),
        "mode": MODE,
        "semantic_enabled": bool(SEM_ENABLED),
        "semantic_threshold": THRESHOLD if SEM_ENABLED else None,
        "latency_budget_ms": BUDGET_MS,
        "ruleset_path": str(RULESET_PATH),
        "directive_hash": DIRECTIVES_HASH,
        "text_sha256": _sha(text),
        "text_len": len(text),
        "verdict": res,
    }
    if LOG_STORE_TEXT:
        entry["text"] = text
    elif LOG_PREVIEW_CHARS > 0:
        preview = text[:LOG_PREVIEW_CHARS]
        if len(text) > LOG_PREVIEW_CHARS:
            preview += "\n\n[...truncated...]\n"
        entry["text_preview"] = preview
    # Use a context manager to avoid file descriptor leaks under sustained runs.
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def _warm_semantic():
    global _PRELOAD_DONE
    if _PRELOAD_DONE:
        return
    try:
        # One dummy call to load model weights and allocations (semantic model import is lazy).
        if SEM_ENABLED:
            from .detectors.mini_semantic import semantic_match
            semantic_match("warmup", ["warmup"], 0.999)
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

    # Fast path: schema-driven deterministic checks excluding semantic similarity.
    t0 = time.perf_counter()
    findings = _validate_directives(text, include_semantic=False, semantic_matcher=None)
    dt_fast = (time.perf_counter() - t0) * 1_000

    res: dict = {"passed": True, "violations": [], "notes": [], "score": 100}
    for f in findings:
        if f.level == "violation":
            res["passed"] = False
            res.setdefault("score", 0)
            res["violations"].append(f"directive_{f.directive_id}")
            res["notes"].append(f"{f.title}: {f.message}")
        else:
            res["notes"].append(f"{f.title}: {f.message}")

    # strict mode blocks on semantic; sync_light returns quickly and may update later.
    dt_sem = None
    if MODE == "strict" and SEM_ENABLED and res.get("passed", True):
        from .detectors.mini_semantic import semantic_match
        t1 = time.perf_counter()
        sem_findings = _validate_directives(text, include_semantic=True, semantic_matcher=semantic_match)
        dt_sem = (time.perf_counter() - t1) * 1_000
        for f in sem_findings:
            if f.level == "violation":
                res["passed"] = False
                res.setdefault("score", 0)
                res["violations"].append(f"directive_{f.directive_id}")
                res["notes"].append(f"{f.title}: {f.message}")
            else:
                res["notes"].append(f"{f.title}: {f.message}")
    elif MODE == "sync_light" and SEM_ENABLED and res.get("passed", True):
        threading.Thread(target=_bg_heavy_check, args=(text, k), daemon=True).start()
        if dt_fast > BUDGET_MS:
            res.setdefault("notes", []).append(f"background_pending:{int(dt_fast)}ms")

    _set(k, res)
    _log_output(text, res)
    _log_latency(MODE, dt_fast, dt_sem, cached=False)
    return res

# ── background hook -----------------------------------------------------
def _bg_heavy_check(text: str, key: str):
    from .detectors.mini_semantic import semantic_match
    sem_findings = _validate_directives(text, include_semantic=True, semantic_matcher=semantic_match)
    blocked = any(f.level == "violation" for f in sem_findings)
    if blocked:
        res: dict = {"passed": False, "score": 0, "violations": [], "notes": []}
        for f in sem_findings:
            if f.level == "violation":
                res["violations"].append(f"directive_{f.directive_id}")
            res["notes"].append(f"{f.title}: {f.message}")
        _set(key, res)
        _log_output(text, res)
