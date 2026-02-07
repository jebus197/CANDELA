"""
guardian_prototype.py
Original “prototype” Guardian that handles directive-bundle loading,
hash verification, and on-chain anchoring.

This version adds thin compatibility wrappers (`guardian_check` and
`guardian`) so that newer runtime layers (guardian_extended /
guardian_runtime) can import it without errors.

No existing functionality has been removed.
"""

from __future__ import annotations
import json, hashlib, pathlib
from typing import Dict

# ── paths --------------------------------------------------------------
ROOT          = pathlib.Path(__file__).resolve().parents[1]
DIRECTIVE_PATH = ROOT / "src" / "directives_schema.json"

# ── core helpers -------------------------------------------------------
def _load_directives() -> list[Dict]:
    with DIRECTIVE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def _bundle_hash(data: list[Dict]) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()

#
# NOTE: Anchoring is handled explicitly via `src/anchor_hash.py` and
# `src/anchor_outputs.py`. The prototype Guardian must NOT auto-anchor a
# modified local directive set on mismatch, because that would undermine the
# idea of a single canonical rule-set.

# ── main prototype API -------------------------------------------------
def guardian_session(text: str) -> dict:
    """
    Prototype enforcement flow:
    1. Verify directive-set integrity (hash match).
    2. (Stub) regex check.
    3. Return verdict structure.
    """
    directives = _load_directives()
    bundle_h   = _bundle_hash(directives)
    KNOWN_HASH = "7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d"

    if bundle_h != KNOWN_HASH:
        verdict = {
            "passed": False,
            "score": 0,
            "violations": ["directive_hash_mismatch"],
            "notes": [f"local directives hash {bundle_h} does not match canonical {KNOWN_HASH}"],
        }
        return verdict

    # All good (content enforcement happens in runtime layers)
    return {"passed": True, "score": 100, "violations": [], "notes": []}

# ── compatibility wrappers ---------------------------------------------
def guardian_check(text: str) -> dict:      # legacy name
    return guardian_session(text)

guardian = guardian_check                  # modern alias expected by runtime
