"""
guardian_extended.py
Extended Guardian logic: directive loading, hashing, validation & LLM session.
"""

from pathlib import Path
import hashlib, json, re
from typing import Tuple, List
from anchor_hash import anchor_hash  # same file as before

DIRECTIVE_FILE = Path(__file__).parent / "directives_schema.json"

# ──────────────────────────────────────────────────────────────────────────
# validate.py-style helpers (imported from Grok PoC, adjusted)
# ──────────────────────────────────────────────────────────────────────────
DIRECTIVE_REGEX_MAP = {
    6: re.compile(r"^Premise: "),
    # add more micro-directive patterns as needed
}

def validate_line(line: str, directive_id: int) -> bool:
    """Return True if a single line satisfies the directive pattern."""
    pattern = DIRECTIVE_REGEX_MAP.get(directive_id)
    return bool(pattern and pattern.match(line))

def validate_response(text: str, directive_ids: List[int]) -> Tuple[bool, List[int]]:
    """
    Check an LLM output block against a list of directive IDs.
    Returns (all_passed, failed_ids)
    """
    failed = [d for d in directive_ids if not any(
        validate_line(l.strip(), d) for l in text.splitlines())]
    return len(failed) == 0, failed
# ──────────────────────────────────────────────────────────────────────────

def load_directives():
    """Return directives JSON and its SHA-256 hash."""
    raw = Path(DIRECTIVE_FILE).read_text(encoding="utf-8")
    d_hash = hashlib.sha256(raw.encode()).hexdigest()
    return json.loads(raw), d_hash

def call_llm(prompt: str) -> str:
    """Stub; plug in your provider here."""
    # Placeholder demo
    return "Premise: Sunlight drives photosynthesis.\nInference: ..."

def guardian_session(prompt: str):
    """Return validated LLM result and directive hash (anchored)."""
    directives, d_hash = load_directives()
    llm_output = call_llm(prompt)

    # Example: ensure micro-directive 6 is respected
    all_ok, failures = validate_response(llm_output, [6])
    if not all_ok:
        raise ValueError(f"Directive check failed IDs: {failures}")

    # anchor hash on chain (tx hash returned but unused here)
    _tx = anchor_hash(d_hash)
    return llm_output, d_hash

if __name__ == "__main__":
    text, h = guardian_session("Explain photosynthesis in one paragraph.")
    print("Output:\n", text)
    print("Directive set hash:", h)
