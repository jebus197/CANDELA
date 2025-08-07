"""
guardian_extended.py
Fast regex guard + hand-off to the existing prototype Guardian.

Works even if guardian_prototype exposes its public entry as either
    • guardian_check(text)          ── original plan
    • guardian(text)                ── current repo state
"""

from __future__ import annotations
import re
from typing import Tuple, Callable
import importlib


# ── 1.  Resolve the underlying Guardian function ──────────────────────────
_proto = importlib.import_module(".guardian_prototype", __package__)
if hasattr(_proto, "guardian_check"):
    _guardian_fn: Callable[[str], Tuple[bool, str]] = _proto.guardian_check
elif hasattr(_proto, "guardian"):
    _guardian_fn = _proto.guardian           # current implementation
else:
    raise ImportError(
        "guardian_prototype.py must expose guardian_check() or guardian()"
    )


# ── 2.  Fast regex blockers ───────────────────────────────────────────────
SAFETY_REGEX_PATTERNS: dict[str, re.Pattern] = {
    "hex_key": re.compile(r"\b0x[a-fA-F0-9]{64}\b"),
    "dob": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+,?\s*\d{2}/\d{2}/\d{4}\b"),
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


# ── 3.  Public entry point ────────────────────────────────────────────────
def guardian(text: str) -> Tuple[bool, str]:
    ok, info = regex_guard(text)
    if not ok:
        return False, f"regex_block:{info}"
    return _guardian_fn(text)


# ── 4.  CLI harness ───────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = input("Paste text to test:\n> ")
    passed, detail = guardian(sample)
    print("✅  PASS" if passed else f"❌  BLOCKED  ({detail})")