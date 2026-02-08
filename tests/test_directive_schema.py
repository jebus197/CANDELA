"""
test_directive_schema.py
------------------------

Ruleset integrity test (reviewer-facing).

What this guarantees:
- src/directives_schema.json exists and is valid JSON
- the canonical SHA-256 of that JSON is recorded in docs/ANCHORS.md

This avoids hard-coding a specific hash in tests while still ensuring the
repository documents the anchored artefact reviewers are expected to verify.
"""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).parent.parent
DIRECTIVES_PATH = ROOT / "src" / "directives_schema.json"
ANCHORS_PATH = ROOT / "docs" / "ANCHORS.md"


def test_directives_schema_load_and_is_anchored():
    assert DIRECTIVES_PATH.exists(), f"Directive schema not found at {DIRECTIVES_PATH}"
    assert ANCHORS_PATH.exists(), f"Anchor log not found at {ANCHORS_PATH}"

    obj = json.loads(DIRECTIVES_PATH.read_text(encoding="utf-8"))
    # Shape can evolve; we only require it to be non-empty JSON.
    assert obj is not None

    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()

    anchors = ANCHORS_PATH.read_text(encoding="utf-8")
    assert re.search(rf"`{digest}`", anchors), (
        "Current directives_schema.json hash is not recorded in docs/ANCHORS.md. "
        "If you intentionally changed the ruleset, re-anchor and log the new hash."
    )
