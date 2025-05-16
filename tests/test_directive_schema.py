import json
import hashlib
from pathlib import Path

# Path to the directive schema (relative to tests/ directory)
DIRECTIVES_PATH = Path(__file__).parent.parent / "src" / "directives_schema.json"
# Known SHA-256 hash for v3.2 as documented in README and Project Brief
KNOWN_HASH_V32 = "3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa"

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
