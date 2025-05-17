#!/usr/bin/env python3
"""
Anchor directives_schema.json hash to Sepolia.
Usage:  python3 src/anchor_hash.py
Env:    SEPOLIA_RPC_URL , SEPOLIA_PRIVATE_KEY
"""

import hashlib
import os
import sys
from pathlib import Path

from web3 import Web3

FILE = Path(__file__).parent / "directives_schema.json"


def sha256_hex(p: Path) -> str:
    """Return the SHA‑256 hex digest of the given file path."""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def send_tx(w3: Web3, data_hex: str) -> str:
    """Send a zero‑value transaction embedding data_hex and return the tx hash."""
    acct = w3.eth.account.from_key(os.environ["SEPOLIA_PRIVATE_KEY"])
    tx = {
        "to": acct.address,
        "value": 0,
        "data": "0x" + data_hex,
        "gas": 30_000,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "maxFeePerGas": w3.to_wei("40", "gwei"),
        "maxPriorityFeePerGas": w3.to_wei("2", "gwei"),
        "chainId": 11155111,  # Sepolia
    }
    signed = acct.sign_transaction(tx)
    return w3.to_hex(w3.eth.send_raw_transaction(signed.rawTransaction))


def main() -> None:
    """Hash directives_schema.json and anchor it on Sepolia."""
    w3 = Web3(Web3.HTTPProvider(os.environ["SEPOLIA_RPC_URL"]))
    if not w3.is_connected():
        sys.exit("RPC not reachable.")
    digest = sha256_hex(FILE)
    tx_hash = send_tx(w3, digest)
    print("SHA-256:", digest)
    print("Tx:", tx_hash)
    print("Etherscan: https://sepolia.etherscan.io/tx/" + tx_hash)


if __name__ == "__main__":
    main()
