"""
guardian_extended.py
Layer-0 safety screen (regex) + existing semantic Guardian.

Structure
---------
1. SAFETY_REGEX_PATTERNS    – fast blockers for obvious leaks/offences
2. regex_guard(text)        – returns (passes, rule_name_or_empty)
3. guardian(text)           – public entry; runs regex then guardian_check
4. CLI test harness         – `python3 src/guardian_extended.py`
"""

from __future__ import annotations

import re
from typing import Tuple

# Import the original semantic layer
from guardian_prototype import guardian_check


# ──────────────────────────────────────────────────────────────
#  1.  FAST REGEX RULES
# ──────────────────────────────────────────────────────────────
SAFETY_REGEX_PATTERNS: dict[str, re.Pattern] = {
    # 64-char Ethereum-style hex strings (risk: private keys)
    "hex_key": re.compile(r"\b0x[a-fA-F0-9]{64}\b"),

    # Name + date-of-birth pattern (risk: personal data leak)
    "dob": re.compile(
        r"\b[A-Z][a-z]+ [A-Z][a-z]+,?\s*\d{2}/\d{2}/\d{4}\b"
    ),

    # Basic profanity (extend as required)
    "profanity": re.compile(
        r"\b(?:damn|shit|fuck|bitch|bastard|asshole|cunt)\b",
        re.IGNORECASE,
    ),
}

# (Optional) map directive IDs → regex patterns.
# If you have directive-specific regex checks, add them here.
DIRECTIVE_REGEX_MAP: dict[str, re.Pattern] = {
    # "D-001": re.compile(r"..."),
    # "D-002": re.compile(r"..."),
}


# ──────────────────────────────────────────────────────────────
#  2.  HELPERS
# ──────────────────────────────────────────────────────────────
def regex_guard(text: str) -> Tuple[bool, str]:
    """
    Returns (passes, rule_name_or_empty).

    *False* means the text is blocked and *rule_name* indicates why.
    """
    for name, pat in SAFETY_REGEX_PATTERNS.items():
        if pat.search(text):
            return False, name

    # Directive-specific scans (optional)
    for did, pat in DIRECTIVE_REGEX_MAP.items():
        if pat.search(text):
            return False, f"directive:{did}"

    return True, ""


# ──────────────────────────────────────────────────────────────
#  3.  PUBLIC ENTRY POINT
# ──────────────────────────────────────────────────────────────
def guardian(text: str) -> Tuple[bool, str]:
    """
    1. Run fast regex screen.
    2. If passed, delegate to semantic guardian_check (existing layer).

    Returns (passes, info).  *info* is empty on success, otherwise the rule.
    """
    ok, info = regex_guard(text)
    if not ok:
        return False, f"regex_block:{info}"

    # Fall through to the original, heavier Guardian
    return guardian_check(text)


# ──────────────────────────────────────────────────────────────
#  4.  CLI HARNESS
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = input("Paste text to test:\n> ")
    passed, detail = guardian(sample)
    if passed:
        print("✅  PASS")
    else:
        print(f"❌  BLOCKED  ({detail})")
