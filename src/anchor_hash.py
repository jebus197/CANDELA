"""
anchor_hash.py
Loads directives → prints SHA-256 → (optionally) posts to Sepolia.
"""

import json, hashlib, os, requests
from pathlib import Path

SCHEMA = Path("src/schema/directives_schema.json")

def main():
    raw = SCHEMA.read_text(encoding="utf-8")
    sha = hashlib.sha256(raw.encode()).hexdigest()
    print(f"Directive SHA-256: {sha}")

    # --- Optional broadcast (disabled by default) ---
    if os.getenv("BROADCAST"):
        wallet = os.getenv("WALLET_ADDR")
        key    = os.getenv("PRIVATE_KEY")
        if not (wallet and key):
            print("Set WALLET_ADDR + PRIVATE_KEY env vars to broadcast.")
            return
        tx_hash = post_to_sepolia(wallet, key, sha)
        print(f"Broadcast TXID: {tx_hash}")

def post_to_sepolia(addr: str, key: str, data: str) -> str:
    # Minimal call via BlockPi
    url = "https://ethereum-sepolia.blockpi.network/v1/rpc/public"
    payload = {
        "jsonrpc":"2.0","method":"eth_sendRawTransaction",
        "params":[f"0x{data}"],"id":1
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()["result"]

if __name__ == "__main__":
    main()
