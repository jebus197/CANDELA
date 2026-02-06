#!/usr/bin/env python3
"""
anchor_outputs.py
Anchor a Merkle root of recent output log entries to Sepolia.

- Reads logs/output_log.jsonl
- Anchors only new lines since last run (tracked in logs/output_anchor_state.json)
- Computes SHA-256 leaves of each JSONL line; pairs hashed to Merkle root
- Sends 0-ETH tx with root in data field
- Appends entry to docs/ANCHORS.md

Env: SEPOLIA_RPC_URL, PRIVATE_KEY (or SEPOLIA_PRIVATE_KEY)
"""

import json, os, hashlib, time
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from eth_account import Account

LOG_FILE = Path("logs/output_log.jsonl")
STATE_FILE = Path("logs/output_anchor_state.json")
ANCHOR_LOG = Path("docs/ANCHORS.md")

load_dotenv()
RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY") or os.getenv("SEPOLIA_PRIVATE_KEY")
if not RPC_URL or not PRIVATE_KEY:
    raise SystemExit("Missing SEPOLIA_RPC_URL and/or PRIVATE_KEY; set in .env")

w3 = Web3(HTTPProvider(RPC_URL))
acct = Account.from_key(PRIVATE_KEY)

if not LOG_FILE.exists():
    raise SystemExit("No output log found at logs/output_log.jsonl; run guardian first.")

STATE_FILE.parent.mkdir(exist_ok=True)
state = {"anchored_lines": 0}
if STATE_FILE.exists():
    state = json.loads(STATE_FILE.read_text())

lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
start = state.get("anchored_lines", 0)
new_lines = lines[start:]
if not new_lines:
    raise SystemExit("No new output entries to anchor.")

# Merkle helpers

def _leaf_hash(line: str) -> bytes:
    return hashlib.sha256(line.encode("utf-8")).digest()

def _merkle_root(hashes: List[bytes]) -> bytes:
    if not hashes:
        return b""
    level = hashes
    while len(level) > 1:
        it = iter(level)
        nxt = []
        for a in it:
            b = next(it, a)  # duplicate last if odd
            nxt.append(hashlib.sha256(a + b).digest())
        level = nxt
    return level[0]

leaves = [_leaf_hash(l) for l in new_lines]
root = _merkle_root(leaves)
root_hex = root.hex()
print(f"Anchoring {len(new_lines)} new entries; Merkle root: {root_hex}")

nonce = w3.eth.get_transaction_count(acct.address)
tx = {
    "to": acct.address,
    "value": 0,
    "gas": 30_000,
    "gasPrice": w3.to_wei("2", "gwei"),
    "nonce": nonce,
    "chainId": 11155111,
    "data": root,
}

signed = acct.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print("⛓️  Sent tx:", tx_hash.hex())
print("⏳  Waiting for confirmation …")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
print(f"✅  Confirmed in block {receipt.blockNumber}")

# log anchor entry
entry = (
    f"- OUTPUT_BATCH lines {start+1}-{start+len(new_lines)} "
    f"→ `{root_hex}` → [{tx_hash.hex()}](https://sepolia.etherscan.io/tx/{tx_hash.hex()})\n"
)
ANCHOR_LOG.touch(exist_ok=True)
with ANCHOR_LOG.open("a", encoding="utf-8") as f:
    f.write(entry)

state["anchored_lines"] = start + len(new_lines)
STATE_FILE.write_text(json.dumps(state, indent=2))
print("📄  Logged to docs/ANCHORS.md and updated state file")
