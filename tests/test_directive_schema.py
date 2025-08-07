"""
test_directive_schema.py
------------------------

Minimal smoke test for CANDELA Proof-of-Concept.

Purpose:
    - Ensures the core directives schema (src/directives_schema.json) is present, valid, non-empty, and unmodified.
    - Computes and compares the schema’s SHA-256 hash against the documented canonical hash for v3.2 PoC.
    - Catches accidental edits, corruption, or schema file removal.

Rationale:
    - In early-stage research/PoC code, this kind of test provides quick confidence that the foundational artifact (the directive set)
      is exactly as intended for reproducible experimentation, even before full test infrastructure or CI is in place.

Usage:
    - Run with pytest from the repo root: `pytest tests/`
    - This test is illustrative but functional and is intended as a template for future, more comprehensive tests.

"""

import json
import hashlib
from pathlib import Path

# Path to the directive schema (relative to tests/ directory)
DIRECTIVES_PATH = Path(__file__).parent.parent / "src" / "directives_schema.json"
# Known SHA-256 hash for v3.2 as documented in README and Project Brief
KNOWN_HASH_V32 = "7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d"
def test_directives_schema_load_and_hash():
    """Test that the directives schema loads and matches the documented hash."""
    # Ensure file exists
    assert DIRECTIVES_PATH.exists(), f"Directive schema not found at {DIRECTIVES_PATH}"

    # Load and check type
    with DIRECTIVES_PATH.open("r", encoding="utf-8") as f:
        directives = json.load(f)
    assert isinstance(directives, list), "Directives schema is not a list"
    assert len(directives) > 0, "Directives schema is empty"

    # Compute hash (keys sorted, Unicode preserved)
    directives_string = json.dumps(directives, sort_keys=True, ensure_ascii=False)
    bundle_hash = hashlib.sha256(directives_string.encode("utf-8")).hexdigest()
    assert bundle_hash == KNOWN_HASH_V32, (
        f"Directive bundle hash mismatch: got {bundle_hash}, expected {KNOWN_HASH_V32}"
    )
