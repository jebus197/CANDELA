"""
guardian_extended.py
Fast safety-regex guard + lazy hand-off to the existing prototype Guardian.

Key change: the underlying Guardian function is resolved **lazily** the first
time `guardian()` is called, so importing this module never crashes unit tests
that only need `regex_guard`.
"""

from __future__ import annotations
import re
import importlib
from typing import Tuple, Callable, Optional

# ── 1.  Fast regex blockers ────────────────────────────────────────────────
SAFETY_REGEX_PATTERNS: dict[str, re.Pattern] = {
    "hex_key": re.compile(r"\b0x[a-fA-F0-9]{64}\b"),
    "dob":     re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+,?\s*\d{2}/\d{2}/\d{4}\b"),
    "profanity": re.compile(
        r"\b(?:damn|shit|fuck|bitch|bastard|asshole|cunt)\b", re.IGNORECASE
    ),
}

def regex_guard(text: str) -> Tuple[bool, str]:
    """Return (passes, rule_name_or_empty)."""
    for name, pat in SAFETY_REGEX_PATTERNS.items():
        if pat.search(text):
            return False, name
    return True, ""


# ── 2.  Lazy resolver for the semantic Guardian ────────────────────────────
_guardian_fn: Optional[Callable[[str], Tuple[bool, str]]] = None

def _resolve_guardian() -> Callable[[str], Tuple[bool, str]]:
    """Find guardian_check() or guardian() inside guardian_prototype.py."""
    proto = importlib.import_module(".guardian_prototype", __package__)
    if hasattr(proto, "guardian_check"):
        return proto.guardian_check              # original plan
    if hasattr(proto, "guardian"):
        return proto.guardian                    # current codebase
    raise ImportError(
        "guardian_prototype.py must expose guardian_check(text) or guardian(text)"
    )


# ── 3.  Public entry point ─────────────────────────────────────────────────
def guardian(text: str) -> dict:
    """
    1. Run fast regex screen.
    2. If passed, delegate to the semantic Guardian (resolved lazily).
    Returns a dict verdict for compatibility with runtime and API layers.
    """
    ok, info = regex_guard(text)
    if not ok:
        return {"passed": False, "score": 0, "violations": ["regex_block"], "notes": [info]}

    global _guardian_fn
    if _guardian_fn is None:            # resolve on first real use
        _guardian_fn = _resolve_guardian()

    return _guardian_fn(text)


# ── 4.  CLI harness (manual testing) ───────────────────────────────────────
if __name__ == "__main__":
    sample = input("Paste text to test:\n> ")
    res = guardian(sample)
    if res.get("passed"):
        print("✅  PASS")
    else:
        detail = ", ".join(res.get("violations", []) + res.get("notes", []))
        print(f"❌  BLOCKED  ({detail})")
