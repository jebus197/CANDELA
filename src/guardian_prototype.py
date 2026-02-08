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
import json, hashlib, pathlib, re
from typing import Dict

# ── paths --------------------------------------------------------------
ROOT          = pathlib.Path(__file__).resolve().parents[1]
DIRECTIVE_PATH = ROOT / "src" / "directives_schema.json"
ANCHORS_PATH = ROOT / "docs" / "ANCHORS.md"

# ── core helpers -------------------------------------------------------
def _load_directives() -> object:
    with DIRECTIVE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def _bundle_hash(data: object) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()

def _latest_anchored_hash() -> str | None:
    if not ANCHORS_PATH.exists():
        return None
    txt = ANCHORS_PATH.read_text(encoding="utf-8")
    # Matches: - `digest` → [tx](...)
    digests = re.findall(r"-\\s+`([0-9a-f]{64})`\\s+→", txt, flags=re.IGNORECASE)
    return digests[-1] if digests else None

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
    known = _latest_anchored_hash()

    if known and bundle_h != known:
        verdict = {
            "passed": False,
            "score": 0,
            "violations": ["directive_hash_mismatch"],
            "notes": [f"local directives hash {bundle_h} does not match last anchored {known} (docs/ANCHORS.md)"],
        }
        return verdict

    # All good (content enforcement happens in runtime layers)
    return {"passed": True, "score": 100, "violations": [], "notes": []}

# ── compatibility wrappers ---------------------------------------------
def guardian_check(text: str) -> dict:      # legacy name
    return guardian_session(text)

guardian = guardian_check                  # modern alias expected by runtime
