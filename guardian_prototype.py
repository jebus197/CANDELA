# guardian_prototype.py
"""
Guardian Prototype
------------------
A minimal middleware that:
1. Loads directive schema and computes its hash
2. (Mock) anchors the hash to a blockchain
3. Combines directives with the user prompt
4. Sends the prompt to an LLM endpoint (mocked here)
5. Validates the response against simple rules
6. Anchors the input/output hash
"""

import json, hashlib, time
import requests  # Only needed once you swap in a real LLM endpoint

DIRECTIVE_FILE = "directives_schema.json"
MAX_RETRIES = 2
# LLM_ENDPOINT = "https://api.openai.com/v1/chat/completions"  # example

# -------- Helper Functions --------------------------------------------------


def load_directives():
    """Return directives list and SHA-256 bundle hash."""
    with open(DIRECTIVE_FILE, "r") as f:
        directives = json.load(f)
    bundle_hash = hashlib.sha256(
        json.dumps(directives, sort_keys=True).encode()
    ).hexdigest()
    return directives, bundle_hash


def blockchain_anchor(bundle_hash, label="directives"):
    """
    Placeholder for anchoring. In production you would POST to an anchoring
    micro-service that writes the hash to Polygon, Ethereum, Hedera, etc.
    """
    ts = int(time.time())
    print(f"[MOCK] Anchoring {label} hash {bundle_hash[:10]}… at {ts}")
    # Example pseudo-call:
    # requests.post("https://anchor-service.xyz/anchor",
    #               json={"label": label, "hash": bundle_hash})
    return {"timestamp": ts, "tx": "0xMOCK" + bundle_hash[:8]}


def merge_prompt(user_prompt, directives):
    """Inject top-level directives into the prompt."""
    top_rules = [d for d in directives if d["id"] in (1, 2, 3)]
    preamble = "\n".join(f"{d['id']}. {d['text']}" for d in top_rules)
    return f"{preamble}\n\nUSER: {user_prompt}"


def call_llm(prompt):
    """Mock LLM call. Replace with real API POST."""
    print("[MOCK] Calling LLM with prompt length", len(prompt))
    # resp = requests.post(LLM_ENDPOINT, headers=..., json=...)
    # return resp.json()["choices"][0]["message"]["content"]
    return "Mock LLM response. Confidence: High"


def validate_response(response):
    """
    Very simple validator:
    - Flags banned words
    - Flags missing 'Confidence:' keyword
    """
    issues = []
    banned = {"fake", "malicious"}
    if any(word in response.lower() for word in banned):
        issues.append("Contains banned word")
    if "confidence:" not in response.lower():
        issues.append("Missing confidence tag")
    return issues


# -------- Session Flow ------------------------------------------------------


def guardian_session(user_prompt):
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

    io_hash = hashlib.sha256(
        json.dumps({"input": prompt, "output": llm_response}, sort_keys=True).encode()
    ).hexdigest()
    blockchain_anchor(io_hash, label="io")

    return {
        "response": llm_response,
        "issues": issues,
        "directive_hash": d_hash,
        "io_hash": io_hash,
    }


if __name__ == "__main__":
    out = guardian_session("Explain photosynthesis in one paragraph.")
    print("\n=== Final Output ===")
    print(json.dumps(out, indent=2))
