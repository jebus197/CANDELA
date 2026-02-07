"""
directive_validation.py

Lightweight, deterministic validation for directives that already have explicit
machine-checkable criteria in `src/directives_schema.json`.

Design goals (v0.3 Research Beta):
- Do NOT change the directive bundle (avoids re-anchoring churn).
- Be explicit about what is enforced vs. what is only documented intent.
- Avoid false positives by only enforcing micro-directive formats when the
  output opts into that structure (e.g., includes "Premise:" / "Inference:").
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


DIRECTIVES_PATH = Path("src/directives_schema.json")

# Canonical v3.2 directive bundle hash (sorted keys, Unicode preserved)
KNOWN_DIRECTIVES_HASH_V32 = "7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d"


@dataclass(frozen=True)
class Finding:
    key: str  # e.g. "6a", "71", "24b"
    level: str  # "violation" | "advisory"
    message: str


def _directive_key(d: dict) -> str:
    # Some directives are broken into micro-steps with the same id and a `sub` field.
    sub = d.get("sub")
    return f"{d.get('id')}{sub}" if sub else str(d.get("id"))


def load_directives(path: Path = DIRECTIVES_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _lines(text: str) -> list[str]:
    return [ln.rstrip() for ln in text.splitlines()]


def _first_nonempty(lines: Iterable[str]) -> Optional[str]:
    for ln in lines:
        if ln.strip():
            return ln.strip()
    return None


def _word_count(s: str) -> int:
    # Simple tokenization suitable for objective limits (<= N words)
    return len([w for w in re.split(r"\s+", s.strip()) if w])


def validate_output(
    text: str,
    *,
    enforce_confidence_tag: bool = False,
    enforce_uncertain_tag: bool = False,
    enforce_microformats: bool = True,
) -> List[Finding]:
    """
    Validate an output string against the subset of directives with explicit criteria.

    Returns a list of Findings. Callers decide whether advisories should block.
    """
    findings: List[Finding] = []
    ls = _lines(text)
    joined = "\n".join(ls)

    # ------------------------------------------------------------------
    # Monitoring: Confidence tag format (Directive 71)
    # ------------------------------------------------------------------
    conf_re = re.compile(r"Confidence:\s*(High|Medium|Low)\b", re.IGNORECASE)
    has_conf = "confidence:" in joined.lower()
    if has_conf:
        if not conf_re.search(joined):
            findings.append(Finding("71", "violation", "Confidence tag present but not in format 'Confidence: High|Medium|Low'."))
    else:
        if enforce_confidence_tag:
            findings.append(Finding("3/71", "violation", "Missing required confidence tag (e.g., 'Confidence: High')."))
        else:
            findings.append(Finding("3/71", "advisory", "No confidence tag found. (Optional unless enforce_confidence_tag=true)"))

    # ------------------------------------------------------------------
    # Uncertainty: [uncertain] tag (Directive 10)
    # ------------------------------------------------------------------
    has_uncertain_tag = "[uncertain]" in joined.lower()
    if enforce_uncertain_tag and not has_uncertain_tag:
        findings.append(Finding("10", "violation", "Missing required [uncertain] tag."))

    # ------------------------------------------------------------------
    # Micro-directive formats (IDs 6, 14, 24)
    # Enforced only when output opts into the structure (marker-based trigger).
    # ------------------------------------------------------------------
    if enforce_microformats:
        lower = joined.lower()

        # ID 6 (Logical-Extension): triggered by Premise:/Inference:
        if any(ln.lstrip().startswith("Premise:") or ln.lstrip().startswith("Inference:") for ln in ls):
            premise_lines = [ln for ln in ls if ln.lstrip().startswith("Premise:")]
            infer_lines = [ln for ln in ls if ln.lstrip().startswith("Inference:")]
            if not premise_lines:
                findings.append(Finding("6a", "violation", "Missing line starting with 'Premise:'."))
            if not infer_lines:
                findings.append(Finding("6b", "violation", "Missing line starting with 'Inference:'."))
            if infer_lines:
                # Apply the <=20 words + ends-with-period to the first Inference line's content.
                content = infer_lines[0].split("Inference:", 1)[1].strip()
                if _word_count(content) > 20:
                    findings.append(Finding("6c", "violation", "Inference content exceeds 20 words."))
                if content and not content.endswith("."):
                    findings.append(Finding("6c", "violation", "Inference content must end with a period."))

        # ID 14 (Associative Reasoning): triggered by Related:
        if any(ln.lstrip().startswith("Related:") for ln in ls):
            idxs = [i for i, ln in enumerate(ls) if ln.lstrip().startswith("Related:")]
            i0 = idxs[0]
            # Next two non-empty lines after Related are treated as steps b and c.
            tail = [ln.strip() for ln in ls[i0 + 1 :] if ln.strip()]
            if not tail:
                findings.append(Finding("14b", "violation", "Missing explanation line after 'Related:'."))
            else:
                if _word_count(tail[0]) > 25:
                    findings.append(Finding("14b", "violation", "Explanation exceeds 25 words."))
            if len(tail) < 2:
                findings.append(Finding("14c", "violation", "Missing practical implication line after explanation."))
            else:
                if _word_count(tail[1]) > 30:
                    findings.append(Finding("14c", "violation", "Practical implication exceeds 30 words."))

        # ID 24 (First-Principles): triggered by explicit marker in output
        # (avoid false positives on arbitrary bullet lists)
        if "first-principles" in lower:
            # Restatement line: first non-empty line after a potential header
            nonempty = [ln.strip() for ln in ls if ln.strip()]
            rest = nonempty[0] if nonempty else ""
            if rest.lower().startswith("first-principles"):
                rest = nonempty[1] if len(nonempty) > 1 else ""
            if rest and _word_count(rest) > 15:
                findings.append(Finding("24a", "violation", "Restatement exceeds 15 words."))

            bullets = [ln.strip() for ln in ls if re.match(r"^[-*]\s+", ln.strip())]
            if len(bullets) != 2:
                findings.append(Finding("24b", "violation", "Expected exactly two bullet points."))

            # For v0.3 we enforce the objective <=100 word limit only.
            if _word_count(" ".join(nonempty)) > 100:
                findings.append(Finding("24c", "violation", "First-principles output exceeds 100 words."))

    return findings

