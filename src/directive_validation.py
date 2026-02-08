"""
directive_validation.py

Schema-driven, deterministic validation for the canonical ruleset in:
  - src/directives_schema.json

Goal:
  - Every directive in the enterprise ruleset has machine-checkable criteria.
  - Enforcement tier is explicit: BLOCK vs WARN.
  - Semantic checks are supported via an injected callback so unit tests stay lightweight.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
import os


ROOT = Path(__file__).resolve().parents[1]
DIRECTIVES_PATH = ROOT / "src" / "directives_schema.json"

# Signature for semantic matching:
# - Return (blocked, reason_string)
SemanticMatcher = Callable[[str, List[str], float], Tuple[bool, str]]

_RULESET_CACHE: Dict[str, Any] | None = None
_RULESET_MTIME: float | None = None


def ruleset_path(default: Path = DIRECTIVES_PATH) -> Path:
    """
    Canonical ruleset path resolution.

    - Default is src/directives_schema.json
    - Override is supported via CANDELA_RULESET_PATH (absolute or repo-relative)
    """
    override = os.getenv("CANDELA_RULESET_PATH")
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        return p
    return default


@dataclass(frozen=True)
class Finding:
    directive_id: int
    title: str
    level: str  # "violation" | "advisory"
    message: str


def load_ruleset(path: Optional[Path] = None) -> Dict[str, Any]:
    global _RULESET_CACHE, _RULESET_MTIME
    if path is None:
        path = ruleset_path()
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        mtime = None
    if _RULESET_CACHE is not None and _RULESET_MTIME == mtime:
        return _RULESET_CACHE

    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        _RULESET_CACHE, _RULESET_MTIME = raw, mtime
        return raw
    # Legacy support: older bundles were a plain list.
    out = {"meta": {"name": "Legacy Ruleset"}, "directives": raw}
    _RULESET_CACHE, _RULESET_MTIME = out, mtime
    return out


def get_directives(ruleset: Dict[str, Any]) -> List[Dict[str, Any]]:
    directives = ruleset.get("directives")
    if not isinstance(directives, list):
        raise TypeError("ruleset.directives must be a list")
    out: List[Dict[str, Any]] = []
    for i, item in enumerate(directives):
        if not isinstance(item, dict):
            raise TypeError(f"Directive at index {i} is not an object/dict")
        out.append(item)
    return out


def canonical_ruleset_sha256(path: Optional[Path] = None) -> str:
    """
    Must match src/anchor_hash.py:
      json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    """
    if path is None:
        path = ruleset_path()
    obj = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _compile_flags(flag_s: str) -> int:
    flags = 0
    for ch in (flag_s or ""):
        if ch.lower() == "i":
            flags |= re.IGNORECASE
        elif ch.lower() == "m":
            flags |= re.MULTILINE
        elif ch.lower() == "s":
            flags |= re.DOTALL
    return flags


def _word_count(s: str) -> int:
    return len([w for w in re.split(r"\s+", s.strip()) if w])


def _luhn_ok(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for i, ch in enumerate(digits):
        n = ord(ch) - 48
        if i % 2 == parity:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


_CARD_CANDIDATE_RE = re.compile(r"(?:\\d[ -]?){13,19}")


def _find_luhn_cards(text: str) -> List[str]:
    hits: List[str] = []
    for m in _CARD_CANDIDATE_RE.finditer(text):
        candidate = m.group(0)
        digits = re.sub(r"[^0-9]", "", candidate)
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            hits.append(digits)
    return hits


def validate_output(
    text: str,
    *,
    ruleset: Optional[Dict[str, Any]] = None,
    include_semantic: bool,
    semantic_matcher: Optional[SemanticMatcher] = None,
) -> List[Finding]:
    """
    Validate text against the schema-driven ruleset.

    - include_semantic controls whether semantic_forbid checks are evaluated.
    - semantic_matcher is required when include_semantic is True.
    """
    rs = ruleset if ruleset is not None else load_ruleset()
    directives = get_directives(rs)

    findings: List[Finding] = []

    for d in directives:
        did = d.get("id")
        if not isinstance(did, int):
            continue

        title = str(d.get("title") or d.get("text") or "").strip() or f"Directive {did}"
        tier = str(d.get("validation_tier") or "BLOCK").strip().upper()
        vc = d.get("validation_criteria") or {}
        checks = vc.get("checks") if isinstance(vc, dict) else None
        if not isinstance(checks, list):
            # Enterprise ruleset requires checks; treat missing checks as an advisory.
            findings.append(Finding(did, title, "advisory", "Directive has no machine-checkable checks."))
            continue

        level = "violation" if tier == "BLOCK" else "advisory"

        for chk in checks:
            if not isinstance(chk, dict):
                continue
            kind = str(chk.get("kind") or "").strip()

            if kind == "regex_forbid":
                pats = chk.get("patterns")
                if not isinstance(pats, list):
                    continue
                for p in pats:
                    if not isinstance(p, dict):
                        continue
                    rx = str(p.get("regex") or "")
                    if not rx:
                        continue
                    flags = _compile_flags(str(p.get("flags") or ""))
                    if re.search(rx, text, flags=flags):
                        pname = str(p.get("name") or "pattern")
                        findings.append(Finding(did, title, level, f"Matched forbidden pattern: {pname}."))

            elif kind == "regex_require":
                rx = str(chk.get("pattern") or "")
                if not rx:
                    continue
                flags = _compile_flags(str(chk.get("flags") or ""))
                if not re.search(rx, text, flags=flags):
                    findings.append(Finding(did, title, level, "Missing required pattern."))

            elif kind == "luhn_card_forbid":
                cards = _find_luhn_cards(text)
                if cards:
                    findings.append(Finding(did, title, level, "Detected a likely payment card number (Luhn-positive)."))

            elif kind == "semantic_forbid":
                if not include_semantic:
                    continue
                if semantic_matcher is None:
                    raise ValueError("include_semantic=True requires semantic_matcher")
                phrases = chk.get("phrases")
                if not isinstance(phrases, list) or not phrases:
                    continue
                phrases_s = [str(x) for x in phrases if str(x).strip()]
                threshold = float(chk.get("threshold") or 0.78)
                blocked, reason = semantic_matcher(text, phrases_s, threshold)
                if blocked:
                    msg = "Semantic similarity matched a prohibited intent."
                    if reason:
                        msg += f" ({reason})"
                    findings.append(Finding(did, title, level, msg))

            elif kind == "max_words":
                n = int(chk.get("n") or 0)
                if n > 0 and _word_count(text) > n:
                    findings.append(Finding(did, title, level, f"Output exceeds {n} words."))

            else:
                # Unknown check kinds should be visible to reviewers.
                findings.append(Finding(did, title, "advisory", f"Unknown check kind: {kind!r}."))

    return findings
