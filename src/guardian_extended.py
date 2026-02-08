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
# Source of truth: src/directives_schema.json (anchored). We precompile the
# BLOCK-tier regex_forbid checks for a fast "first pass".
def _compile_ruleset_patterns() -> dict[str, re.Pattern]:
    try:
        from .directive_validation import load_ruleset, get_directives

        ruleset = load_ruleset()
        directives = get_directives(ruleset)
        out: dict[str, re.Pattern] = {}

        def _flags(flag_s: str) -> int:
            flags = 0
            for ch in (flag_s or ""):
                if ch.lower() == "i":
                    flags |= re.IGNORECASE
                elif ch.lower() == "m":
                    flags |= re.MULTILINE
                elif ch.lower() == "s":
                    flags |= re.DOTALL
            return flags

        for d in directives:
            tier = str(d.get("validation_tier") or "").upper()
            if tier != "BLOCK":
                continue
            vc = d.get("validation_criteria") or {}
            checks = vc.get("checks") if isinstance(vc, dict) else None
            if not isinstance(checks, list):
                continue
            for chk in checks:
                if not isinstance(chk, dict) or chk.get("kind") != "regex_forbid":
                    continue
                pats = chk.get("patterns")
                if not isinstance(pats, list):
                    continue
                for p in pats:
                    if not isinstance(p, dict):
                        continue
                    name = str(p.get("name") or "").strip()
                    rx = str(p.get("regex") or "")
                    if not name or not rx:
                        continue
                    out[name] = re.compile(rx, _flags(str(p.get("flags") or "")))
        return out
    except Exception:
        # Last-resort fallback: tiny default set, keeps CLI harness usable.
        return {
            "eth_private_key_hex": re.compile(r"\b0x[a-fA-F0-9]{64}\b"),
        }


SAFETY_REGEX_PATTERNS: dict[str, re.Pattern] = _compile_ruleset_patterns()

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
