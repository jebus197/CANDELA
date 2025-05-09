```python
"""
guardian_extended.py
--------------------
Richer illustrative workflow for CANDELA.

Adds:
* Error handling for missing directive file & token budget overflow
* Placeholder for real LLM call via requests
* Template Web3 anchoring (commented)
* More detailed validation logic
"""

import json, hashlib, os, sys, time, requests
from pathlib import Path
# from web3 import Web3  # Uncomment when anchoring to Polygon

DIRECTIVE_FILE = Path(__file__).parent / "directives_schema.json"
MAX_RETRIES = 2
TOKEN_BUDGET = 8000


# ---------- Helper functions -----------------------------------------------
def load_directives():
    """Load directives & hash; exit if file missing or JSON invalid."""
    if not DIRECTIVE_FILE.exists():
        sys.exit("Directive schema not found.")
    try:
        directives = json.loads(DIRECTIVE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"JSON error in directives file: {e}")
    bundle_hash = hashlib.sha256(json.dumps(directives, sort_keys=True).encode()).hexdigest()
    return directives, bundle_hash


def blockchain_anchor(bundle_hash: str, label: str = "directives"):
    """Mock anchoring; replace with real Web3 call when ready."""
    ts = int(time.time())
    print(f"[MOCK] Anchoring {label} hash {bundle_hash[:10]}… at {ts}")
    # Example Web3 code (commented):
    # w3 = Web3(Web3.HTTPProvider(os.getenv("POLYGON_RPC")))
    # acct = w3.eth.account.from_key(os.getenv("ANCHOR_PRIVATE_KEY"))
    # tx = {
    #     "to": "0x0000000000000000000000000000000000000000",
    #     "value": 0,
    #     "gas": 21000,
    #     "data": bundle_hash.encode(),
    #     "nonce": w3.eth.get_transaction_count(acct.address)
    # }
    # signed = acct.sign_transaction(tx)
    # tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # return tx_hash.hex()
    return {"timestamp": ts, "tx": f"0xMOCK{bundle_hash[:8]}"}


def merge_prompt(user_prompt: str, directives):
    """Inject top-level directives; error if prompt gets too long."""
    top_rules = [d for d in directives if d["id"] in (1, 2, 3)]
    preamble = "\n".join(f"{d['id']}. {d['text']}" for d in top_rules)
    combined = f"{preamble}\n\nUSER: {user_prompt}"
    if len(combined) > TOKEN_BUDGET:
        raise ValueError("Prompt exceeds token budget.")
    return combined


def call_llm(prompt: str) -> str:
    """Placeholder; swap in real LLM POST."""
    print("[MOCK] Would call real LLM here; prompt length:", len(prompt))
    # Example OpenAI call (commented):
    # resp = requests.post(
    #     "https://api.openai.com/v1/chat/completions",
    #     headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
    #     json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    # )
    # return resp.json()["choices"][0]["message"]["content"]
    return "Regenerated answer. Confidence: Medium"


def validate_response(response: str):
    """Check banned words & presence of confidence tag."""
    issues = []
    banned = {"malicious", "fake"}
    if any(word in response.lower() for word in banned):
        issues.append("Contains banned word")
    if "confidence:" not in response.lower():
        issues.append("Missing confidence tag")
    return issues


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
        prompt += f"\n\nSystem: Regenerate. Issues: {issues}"
        attempt += 1

    io_hash = hashlib.sha256(json.dumps({"input": prompt, "output": llm_response}, sort_keys=True).encode()).hexdigest()
    blockchain_anchor(io_hash, label="io")

    return {"response": llm_response, "issues": issues, "directive_hash": d_hash, "io_hash": io_hash}


if __name__ == "__main__":
    print(json.dumps(guardian_session("Give a two-line summary of quantum entanglement."), indent=2))
```
