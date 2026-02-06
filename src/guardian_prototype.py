"""
guardian_prototype.py
Original “prototype” Guardian that handles directive-bundle loading,
hash verification, and on-chain anchoring.

This version adds thin compatibility wrappers (`guardian_check` and
`guardian`) so that newer runtime layers (guardian_extended /
guardian_runtime) can import it without errors.

No existing functionality has been removed.
"""

from __future__ import annotations
import json, hashlib, pathlib, datetime
from typing import Dict

# ── paths --------------------------------------------------------------
ROOT          = pathlib.Path(__file__).resolve().parents[1]
DIRECTIVE_PATH = ROOT / "src" / "directives_schema.json"
ANCHOR_LOG     = ROOT / "docs" / "ANCHORS.md"

# ── config -------------------------------------------------------------
SEPOLIA_RPC   = "https://sepolia.infura.io/v3/your-infura-key"
WALLET_PRIV   = "0xYOUR_PRIVATE_KEY"

# ── core helpers -------------------------------------------------------
def _load_directives() -> list[Dict]:
    with DIRECTIVE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def _bundle_hash(data: list[Dict]) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()

def _anchor_on_chain(h: str) -> str:
    """Write hash to Sepolia. Returns tx hash."""
    if WALLET_PRIV.lower().startswith("0xyour_private_key"):
        print(f"[INFO] (dev) skip anchor {h[:8]}… (placeholder key)")
        return "0xDEV_SKIP"
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
    acct = w3.eth.account.from_key(WALLET_PRIV)
    tx = {
        "from": acct.address,
        "to": acct.address,  # self-send; data holds the hash
        "value": 0,
        "data": h.encode(),
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 30_000,
        "gasPrice": w3.to_wei("5", "gwei"),
        "chainId": 11155111,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return w3.to_hex(tx_hash)

def _log_anchor(h: str, tx_hex: str):
    AnchorLine = (
        f"- `{h}` → "
        f"[{tx_hex}](https://sepolia.etherscan.io/tx/{tx_hex}) "
        f"({datetime.date.today()})\n"
    )
    ANCHOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not ANCHOR_LOG.exists():
        ANCHOR_LOG.write_text("# Directive-set Anchors\n\n")
    with ANCHOR_LOG.open("a", encoding="utf-8") as f:
        f.write(AnchorLine)

# ── main prototype API -------------------------------------------------
def guardian_session(text: str) -> dict:
    """
    Prototype enforcement flow:
    1. Verify directive-set integrity (hash match).
    2. (Stub) regex check.
    3. Return verdict structure.
    """
    directives = _load_directives()
    bundle_h   = _bundle_hash(directives)
    KNOWN_HASH = "7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d"

    if bundle_h != KNOWN_HASH:
        # Integrity breach – anchor new hash and warn
        tx_hex = _anchor_on_chain(bundle_h)
        _log_anchor(bundle_h, tx_hex)
        verdict = {
            "passed": False,
            "score": 0,
            "violations": ["directive_hash_mismatch"],
            "notes": [f"anchored {bundle_h[:8]}.. to Sepolia ({tx_hex[:10]}..)"],
        }
        return verdict

    # Very simple placeholder check
    lowered = text.lower()
    if any(bad in lowered for bad in ("bomb", "explosive", "hurt myself")):
        return {"passed": False, "score": -50, "violations": ["regex_block"], "notes": []}

    # All good
    return {"passed": True, "score": 100, "violations": [], "notes": []}

# ── compatibility wrappers ---------------------------------------------
def guardian_check(text: str) -> dict:      # legacy name
    return guardian_session(text)

guardian = guardian_check                  # modern alias expected by runtime
