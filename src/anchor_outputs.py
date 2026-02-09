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

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from eth_account import Account

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

def _append_anchor_entry(anchor_log: Path, entry: str) -> None:
    anchor_log.parent.mkdir(parents=True, exist_ok=True)
    anchor_log.touch(exist_ok=True)
    existing = anchor_log.read_text(encoding="utf-8")
    if entry in existing:
        return
    marker = "## Output batch anchors"
    if marker in existing:
        head, tail = existing.split(marker, 1)
        new_tail = marker + "\n\n" + entry + tail.lstrip("\n")
        anchor_log.write_text(head + new_tail, encoding="utf-8")
        return
    with anchor_log.open("a", encoding="utf-8") as f:
        f.write(entry)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Anchor a Merkle root of recent CANDELA output log entries to Sepolia.",
    )
    p.add_argument(
        "--log",
        default="logs/output_log.jsonl",
        help="Path to output_log.jsonl (default: logs/output_log.jsonl).",
    )
    p.add_argument(
        "--state",
        default="logs/output_anchor_state.json",
        help="Path to anchor state file (default: logs/output_anchor_state.json).",
    )
    p.add_argument(
        "--anchors",
        default="docs/ANCHORS.md",
        help="Path to ANCHORS.md (default: docs/ANCHORS.md).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute the Merkle root and print it, but do not send any transaction.",
    )
    args = p.parse_args()

    log_file = Path(args.log)
    state_file = Path(args.state)
    anchor_log = Path(args.anchors)

    load_dotenv()
    rpc_url = os.getenv("SEPOLIA_RPC_URL")
    private_key = os.getenv("PRIVATE_KEY") or os.getenv("SEPOLIA_PRIVATE_KEY")
    if not rpc_url or not private_key:
        print("ERROR: Missing SEPOLIA_RPC_URL and/or PRIVATE_KEY (or SEPOLIA_PRIVATE_KEY).")
        print("Set these in a local .env file. (Do not commit .env to Git.)")
        return 2

    if not log_file.exists():
        print(f"ERROR: No output log found at {log_file}. Run the guardian first.")
        return 2

    state_file.parent.mkdir(parents=True, exist_ok=True)
    state = {"anchored_lines": 0}
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))

    lines = log_file.read_text(encoding="utf-8").splitlines()
    start = int(state.get("anchored_lines", 0) or 0)
    new_lines = lines[start:]
    if not new_lines:
        print("No new output entries to anchor.")
        return 0

    leaves = [_leaf_hash(l) for l in new_lines]
    root = _merkle_root(leaves)
    root_hex = root.hex()
    print(f"New entries: {len(new_lines)} (lines {start+1}-{start+len(new_lines)})")
    print(f"Merkle root: {root_hex}")
    if args.dry_run:
        print("Dry run: no transaction sent.")
        return 0

    w3 = Web3(HTTPProvider(rpc_url))
    acct = Account.from_key(private_key)

    try:
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
        tx_hex = tx_hash.hex()
        print(f"Sent tx: {tx_hex}")
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        print(f"Confirmed in block {receipt.blockNumber}")
    except Exception as e:
        # Keep the output reviewer-friendly. Root is still printed, state is not advanced.
        msg = str(e).strip() or e.__class__.__name__
        print("ERROR: Failed to send/confirm the anchor transaction.")
        print("This is usually a network/DNS/RPC provider issue, not a CANDELA logic failure.")
        print(f"Details: {msg}")
        print("Nothing was anchored; your anchor state was not advanced.")
        return 3

    # Log anchor entry + update state only after success.
    entry = (
        f"- OUTPUT_BATCH lines {start+1}-{start+len(new_lines)} "
        f"→ `{root_hex}` → [{tx_hex}](https://sepolia.etherscan.io/tx/{tx_hex})\n"
    )
    _append_anchor_entry(anchor_log, entry)
    state["anchored_lines"] = start + len(new_lines)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"Logged to {anchor_log} and updated {state_file}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
