# CANDELA – Technical Specification (v 0.1)

**Purpose**  
Provide a middleware (**Directive Guardian**) that enforces and audits a machine‑readable directive set for any LLM, hashing both the rule‑set and each input/output bundle to a public blockchain for immutability and provenance.

---

## 1 High‑Level Architecture

User → **Guardian Middleware** → LLM API → **Guardian Validator** → Blockchain Anchor

1. **Guardian Loader** — loads `directives_schema.json`, computes SHA‑256 hash, and confirms it matches the anchored reference.  
2. **Prompt Builder** — prepends top‑level directives (IDs 1‑3) and any micro‑directives the validator will test.  
3. **LLM Caller** — sends the prompt to an external LLM (OpenAI, Gemini, etc.).  
4. **Validator** — runs directive‑specific checks on the LLM response.  
5. **Anchor Service** — writes hashes of the directive bundle and the I/O bundle to the Polygon testnet (or another chain).

---

## 2 Repository Structure

| Path | Purpose |
|------|---------|
| `docs/` | Directive PDFs, FAQ, diagrams |
| `src/guardian_prototype.py` | Minimal runnable PoC (≈ 200 LOC) |
| `src/guardian_extended.py` | Richly commented flow with error handling & anchoring stub |
| `src/directives_schema.json` | Machine‑readable directive list (v 3.2, 76 items) |
| `requirements.txt` | Python dependencies (`requests`; `web3.py` optional) |
| `TECH_SPEC.md` | *This* specification |
| `tests/` | Placeholder for unit tests |

> **Note:** all paths are relative to the repository root.

---

## 3 Dependencies & Setup

```bash
git clone https://github.com/yourname/candela-llm-layer.git
cd candela-llm-layer
pip install -r requirements.txt

# Optional blockchain anchoring
pip install web3
export ANCHOR_PRIVATE_KEY="your-testnet-private-key"
```

---

## 4 Guardian Workflow (Extended Version)

| Step | Function | Implementation | Validation / Notes |
|------|----------|----------------|--------------------|
| 1 | Load directives & compute hash | `load_directives()` | Abort if hash mismatch |
| 2 | Anchor directive hash | `blockchain_anchor(label="directives")` | Must return tx receipt |
| 3 | Build prompt | `merge_prompt()` | Raises error if token budget exceeded |
| 4 | Call LLM | `call_llm()` | Uses `OPENAI_API_KEY` |
| 5 | Validate response | `validate_response()` | Returns list of issues |
| 6 | Retry loop | `guardian_session()` | ≤ `MAX_RETRIES` |
| 7 | Anchor I/O hash | `blockchain_anchor(label="io")` | Same chain as step 2 |

---

## 5 Directive Validation Overview

* **Concrete micro‑directives** (e.g., 6a‑c, 24a‑c) specify regex or structural checks.  
* **Abstract directives** (e.g., #2 “Do no harm”) will require a policy engine or a human audit flag in a future release.  
* Validation results are appended to the final JSON summary (`issues` field).

---

## 6 File Descriptions

### 6.1 `src/directives_schema.json`
* Canonical machine‑readable source (IDs, text, notes, validation criteria).  
* Any change here requires:  
  1. Incrementing the semantic version (e.g., 0.1 → 0.2).  
  2. Re‑anchoring the directive hash on‑chain.  
  3. Updating the `README` and commit hash reference.

### 6.2 `src/guardian_prototype.py`
* ≤ 200 lines, standard‑library only.  
* Demonstrates end‑to‑end flow with mock anchoring and a trivial validator.  
* Good for smoke tests and CI.

### 6.3 `src/guardian_extended.py`
* Adds:  
  - Error handling for missing file or token‑budget overflow.  
  - Placeholder for real LLM call via `requests`.  
  - Template Web3 anchoring (commented).  
  - Rich debug prints.  
* Intended starting point for contributors.

### 6.4 `docs/FAQ.md`
Explains project goals to non‑technical stakeholders and is linked from the `README`.

---

## 7 Blockchain Anchoring Details

### 7.1 Chain choice  
Polygon Mumbai testnet is chosen for low fees and EVM compatibility. Production may migrate to Polygon mainnet, Hedera, or Filecoin.

### 7.2 Contract‑less anchoring  
Each anchor is a zero‑value transaction whose `data` field contains the SHA‑256 hash.

* **Advantages**  
  * Simplicity (no contract deployment)  
  * Universal verification via any block explorer

### 7.3 Anchor function (sample)

```python
from web3 import Web3
import os

def anchor_hash(hash_hex: str) -> str:
    w3 = Web3(Web3.HTTPProvider(os.getenv("POLYGON_RPC")))
    acct = w3.eth.account.from_key(os.getenv("ANCHOR_PRIVATE_KEY"))
    tx = {
        "to": "0x0000000000000000000000000000000000000000",
        "value": 0,
        "gas": 21_000,
        "data": hash_hex.encode(),
        "nonce": w3.eth.get_transaction_count(acct.address)
    }
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()
```

*Future work:* wrap this in a tiny REST micro‑service so Guardian scripts stay lightweight.

---

## 8 Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | API key for real LLM call |
| `POLYGON_RPC` | RPC endpoint (e.g., `https://rpc-mumbai.maticvigil.com`) |
| `ANCHOR_PRIVATE_KEY` | Hot‑wallet key (testnet) |
| `MAX_RETRIES` | Optional override for default retry count |

---

## 9 Unit Testing Plan

Framework: **pytest**

| Test | Purpose |
|------|---------|
| Hash Integrity | Ensure schema hash equals anchored reference |
| Prompt Merge | Assert top‑level directives are present |
| Validator | Feed canned LLM outputs to validate directive pass/fail |
| Retry Logic | Simulate banned‑word response; expect regenerate |

The CI pipeline (GitHub Actions) will run tests on every pull request.

---

## 10 Developer To‑Do (v 0.1 tidy‑ups)

1. **Remove unused imports** in `guardian_prototype.py`.  
2. **Real LLM integration**: implement `call_llm` HTTP POST; read API key from `OPENAI_API_KEY`.  
3. **Validation expansion**: translate regex criteria for IDs 6a‑c, 24a‑c, 71‑73.  
4. **Blockchain anchoring**: replace mock print with `anchor_hash()` using the Polygon testnet (directive hash and I/O hash).  
5. **Unit tests**: add pytest scripts in `tests/`; ensure CI passes before merging.  
6. **Documentation**: add an architecture diagram (PNG) to `docs/`; update `README` badge with latest commit hash and anchor TX link.

---

## 11 Versioning & Anchoring Policy

| Event | Version bump | Action |
|-------|--------------|--------|
| Change to directive text / IDs | 0.1 → 0.2 (minor) | Recompute bundle hash; anchor; update docs |
| Code refactor (no directive change) | 0.1 → 0.1.1 (patch) | No re‑anchor required |
| New directive added | Minor bump | Update tests & docs; anchor new hash |
| Breaking schema change | 1.x (major) | Migrate validation harness; anchor new hash |

---

## 12 Security Considerations

* **Hot‑wallet risk** – keep only minimal MATIC in the testnet wallet.  
* **Prompt injection** – future work: sandbox user input before merging.  
* **API‑key leakage** – store credentials in GitHub repo secrets for CI.

---

## 13 Governance Roadmap

1. **Phase 1** – Maintainer‑led repository (current).  
2. **Phase 2** – Community advisory group (Telegram/Discord).  
3. **Phase 3** – DAO votes on directive updates; smart‑contract commit‑reveal scheme.

---

## 14 Contact

Create issues on GitHub or e‑mail `<maintainer@example.com>`. A Discord link will be added once the community reaches 5 contributors.
