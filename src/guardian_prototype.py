"""
guardian_prototype.py
---------------------
Minimal runnable proof-of-concept for CANDELA.

Flow:
1. Load directives_schema.json, compute SHA-256 hash
2. Mock-anchor the hash (print statement)
3. Merge top-level directives (IDs 1-3) with user prompt
4. Call a placeholder LLM function
5. Validate response for a confidence tag
6. Anchor input/output hash (mock)
"""

import json, hashlib, time, os, sys
from pathlib import Path

DIRECTIVE_FILE = Path(__file__).parent / "directives_schema.json"
MAX_RETRIES = 2


# ---------- Helper functions ------------------------------------------------
def load_directives():
    """Return directives list and SHA-256 bundle hash."""
    try:
        directives = json.loads(Path(DIRECTIVE_FILE).read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit("Directive schema not found.")
    bundle_hash = hashlib.sha256(json.dumps(directives, sort_keys=True).encode()).hexdigest()
    return directives, bundle_hash


def blockchain_anchor(bundle_hash: str, label: str = "directives"):
    """Mock anchoring (prints); replace with real web3 call in guardian_extended."""
    ts = int(time.time())
    print(f"[MOCK] Anchoring {label} hash {bundle_hash[:10]}… at {ts}")
    return {"timestamp": ts, "tx": f"0xMOCK{bundle_hash[:8]}"}


def merge_prompt(user_prompt: str, directives):
    top_rules = [d for d in directives if d["id"] in (1, 2, 3)]
    preamble = "\n".join(f"{d['id']}. {d['text']}" for d in top_rules)
    return f"{preamble}\n\nUSER: {user_prompt}"


def call_llm(prompt: str) -> str:
    """Placeholder LLM call — replace with real HTTP POST."""
    print("[MOCK] Calling LLM (placeholder).")
    return "Mock response. Confidence: High"


def validate_response(response: str):
    """Basic validator: require the word 'Confidence:'."""
    return [] if "confidence:" in response.lower() else ["Missing confidence tag"]


# ---------- Main guardian session ------------------------------------------
def guardian_session(user_prompt: str):
    directives, d_hash = load_directives()
    blockchain_anchor(d_hash, label="directives")

    prompt = merge_prompt(user_prompt, directives)
    attempt = 0
    while attempt <= MAX_RETRIES:
        llm_response = call_llm(prompt)
        issues = validate_response(llm_response)
        if not issues:
            break
        prompt += f"\n\nSystem: Regenerate. Issues detected: {issues}"
        attempt += 1

    io_hash = hashlib.sha256(json.dumps({"input": prompt, "output": llm_response}, sort_keys=True).encode()).hexdigest()
    blockchain_anchor(io_hash, label="io")

    return {"response": llm_response, "issues": issues, "directive_hash": d_hash, "io_hash": io_hash}


if __name__ == "__main__":
    result = guardian_session("Explain photosynthesis in one paragraph.")
    print("\n=== Final Output ===")
    print(json.dumps(result, indent=2))
