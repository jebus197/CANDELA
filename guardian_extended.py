"""
guardian_extended.py
Fast regex screen that runs *before* the semantic Guardian checks.
Return True  = text passes.
Return False = text fails and includes the rule that triggered.
"""

import re
from guardian_prototype import guardian_check  # keeps your original logic

# ------------  SIMPLE REGEX RULES  ------------ #

PATTERNS = {
    # 64-char Ethereum-style hex strings (risk: private keys)
    "hex_key": re.compile(r"\b0x[a-fA-F0-9]{64}\b"),

    # Name + date-of-birth pattern (risk: personal data leak)
    "dob": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+,?\s*\d{2}/\d{2}/\d{4}\b"),

    # Basic profanity list (extend as needed)
    "profanity": re.compile(
        r"\b(?:damn|shit|fuck|bitch|bastard|asshole|cunt)\b", re.IGNORECASE
    ),
}


def regex_guard(text: str) -> tuple[bool, str]:
    """Return (pass/fail, rule_name_or_empty)."""
    for rule, pat in PATTERNS.items():
        if pat.search(text):
            return False, rule
    return True, ""


# ------------  PUBLIC ENTRY POINT  ------------ #

def guardian(text: str) -> tuple[bool, str]:
    """
    1. Fast regex scan.
    2. Full semantic guardian_check only if regex passes.
    """
    ok, rule = regex_guard(text)
    if not ok:
        return False, f"regex_block:{rule}"

    return guardian_check(text)  # (bool, explanation)

# CLI helper ------------------------------------------------------------

if __name__ == "__main__":
    sample = input("Paste text to test: ")
    passed, info = guardian(sample)
    print("✅ PASS" if passed else f"❌ BLOCKED ({info})")
