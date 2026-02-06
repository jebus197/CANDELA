#!/usr/bin/env python3
"""
anchor_hash.py
Anchor the current SHA-256 of src/directives_schema.json to Ethereum Sepolia.

• Reads the directives file
• Computes SHA-256
• Sends a 0-ETH transaction whose data field is that hash
• Prints tx hash and waits for 1 confirmation
"""

import os
import json
import time
import hashlib
from pathlib import Path

from web3 import Web3, HTTPProvider
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# 1. Environment / config                                                     #
# --------------------------------------------------------------------------- #

load_dotenv()                                                     # .env file

RPC_URL      = os.getenv("SEPOLIA_RPC_URL")                      # Alchemy URL
PRIVATE_KEY  = os.getenv("PRIVATE_KEY") or os.getenv("SEPOLIA_PRIVATE_KEY")
DIR_FILE     = Path("src/directives_schema.json")                # Rule-set

if not RPC_URL or not PRIVATE_KEY:
    raise SystemExit(
        "Missing SEPOLIA_RPC_URL and/or PRIVATE_KEY (or SEPOLIA_PRIVATE_KEY). "
        "Add them to a .env file in the repo root."
    )

w3 = Web3(HTTPProvider(RPC_URL))
acct = Account.from_key(PRIVATE_KEY)

# --------------------------------------------------------------------------- #
# 2. Compute SHA-256                                                          #
# --------------------------------------------------------------------------- #

# Canonical JSON hash (sorted keys, Unicode preserved) to match tests/docs
directives = json.loads(DIR_FILE.read_text(encoding="utf-8"))
canonical = json.dumps(directives, sort_keys=True, ensure_ascii=False).encode("utf-8")
digest = hashlib.sha256(canonical).hexdigest()
print("Directive SHA-256:", digest)

# --------------------------------------------------------------------------- #
# 3. Build & sign transaction                                                 #
# --------------------------------------------------------------------------- #

nonce   = w3.eth.get_transaction_count(acct.address)
tx      = {
    "to"      : acct.address,        # self-send 0 ETH
    "value"   : 0,
    "gas"     : 30_000,
    "gasPrice": w3.to_wei("2", "gwei"),
    "nonce"   : nonce,
    "chainId" : 11155111,            # Sepolia
    "data"    : bytes.fromhex(digest)  # embed the hash (raw bytes)
}

signed = acct.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)    # v6 attr

print("⛓️  Sent tx:", tx_hash.hex())

# --------------------------------------------------------------------------- #
# 4. Wait 1 confirmation                                                      #
# --------------------------------------------------------------------------- #

print("⏳  Waiting for confirmation …")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
print(f"✅  Confirmed in block {receipt.blockNumber}")

# --------------------------------------------------------------------------- #
# 5. Dump minimal anchor record (optional)                                    #
# --------------------------------------------------------------------------- #

ANCHOR_LOG = Path("docs/ANCHORS.md")
entry = f"- `{digest}` → [{tx_hash.hex()}](https://sepolia.etherscan.io/tx/{tx_hash.hex()})\n"
ANCHOR_LOG.touch(exist_ok=True)
existing = ANCHOR_LOG.read_text(encoding="utf-8")
if entry not in existing:
    with ANCHOR_LOG.open("a", encoding="utf-8") as f:
        f.write(entry)
print("📄  Logged to docs/ANCHORS.md")
