# CANDELA – Project Brief (Updated for v0.3 - Feb 2026)

**CANDELA: Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

## Elevator Pitch

**CANDELA adds a blockchain-anchored "Directive Guardian" layer in front of any model endpoint (e.g., an LLM). It transforms often fragile prompt rules and behavioral guidelines into a verifiable and auditable governance system.**

---

## The Problem: Unreliable & Opaque AI

Current AI models (including LLMs), while incredibly powerful, often exhibit unpredictable behavior. They can produce incorrect information ("hallucinate"), deviate from instructions ("drift"), and their internal decision-making processes are largely opaque ("black boxes"). This lack of inherent reliability and transparency poses significant risks, limiting their trustworthiness for critical applications and making true accountability difficult to achieve.

## CANDELA's Solution: Verifiable Pre-Execution Governance

CANDELA introduces the **"Directive Guardian,"** a middleware software component designed to sit between a user (or application) and a model endpoint. The Guardian enforces a predefined, human-readable set of behavioral and cognitive rules called the **"Directive Scaffold."**

The core principles are:

1.  **Defined Rule-Set:** The canonical ruleset is stored in a machine-readable JSON format (`src/directives_schema.json`).
2.  **Integrity via Blockchain Anchoring:** Before the Guardian uses these directives, it calculates a unique cryptographic fingerprint (SHA-256 hash) of the entire directive set. This hash is then recorded ("anchored") on a public blockchain testnet (e.g., Polygon Mumbai or Ethereum Sepolia). This creates an immutable, publicly verifiable record of the exact rule-set that *should* be in force.
3.  **Runtime Verification:** The Guardian computes the canonical SHA-256 of the local ruleset and records it in every audit log entry. Reviewers can compare that hash to the on-chain anchor listed in `docs/ANCHORS.md`.
4.  **Guided Model Output:** The Guardian strategically incorporates the verified directives into prompts sent to the model.
5.  **Automated Validation:** The Guardian checks text outputs against the machine-checkable criteria in the ruleset (BLOCK and WARN tiers).
6.  **Accountability Loop:** The system enables an auditable trail from the enforced rules to the model’s behavior, with options to also anchor hashes of interactions.

---

## Key Innovations & Benefits

* **Pre-Execution Rule Verification:** Ensures the governing rule-set's integrity *before* the model generates output.
* **Micro-Directives:** Decomposes complex abstract concepts (like "First-Principles Reasoning") into smaller, concrete, and more easily testable steps for the model and Guardian.
* **Transparency & Auditability:** Human-readable directives coupled with blockchain-anchored verification provide unprecedented oversight.
* **Enhanced Model Reliability:** Aims to reduce hallucinations, instructional drift, and inconsistencies.
* **Open & Model-Agnostic Potential:** Designed as an open-source (MIT licensed) middleware layer.
* **Addressing "AI Slop" & Supporting Content Creators (Future Vision):** The framework's principles could be extended to verify human-generated content against defined standards, potentially combating low-quality "AI slop" and enabling fairer monetization for original creators.

---

## Current Status (v0.3 — Feb 2026)

* **Guardian:** Regex + MiniLM (`all-MiniLM-L6-v2`) semantic checks with caching (`src/guardian_runtime.py`). Modes: `strict` (default, blocks until semantic passes), `sync_light` (asynchronous semantic), `regex_only` (no semantic). Warm preload prevents first-call stalls; latency is logged.
* **Ruleset:** `src/directives_schema.json` (Enterprise E1.0, 12 directives; no N/A criteria) — canonical SHA-256 `bddd2587745d1d86a4d14cf006025386a218e4550642ca236ca6b682125e3f6a` (anchor recorded in `docs/ANCHORS.md`).
* **Output provenance:** Every checked output is logged off-chain, batched into a Merkle root, and anchored on-chain via `src/anchor_outputs.py` (entries recorded in `docs/ANCHORS.md`). Individual outputs can be proven later via Merkle proof.
* **Docs/DOI:** OSF DOI 10.17605/OSF.IO/3S7BT; Tech Spec/README/Roadmap aligned to v0.3; reviewer bundle available.

## The Guardian (letter, spirit, receipt)

1) **Letter of the law (explicit compliance).** Regex/structural rules act like non‑negotiable clauses; violations block immediately and the rule-set is anchored on-chain.  
2) **Spirit of the law (semantic intent).** MiniLM (`all-MiniLM-L6-v2`) reads context to catch evasive or malicious intent beyond keywords. Mode is configurable to balance security vs. throughput.  
3) **Digital receipt (forensic proof).** Outputs stay off-chain but are logged, Merklized, and only the root is anchored. You can later reveal one output + its proof to show it existed unaltered at that time, without paying per-output gas or leaking content.

## Key Components (v0.3)

1. **Guardian runtime:** `src/guardian_runtime.py` (regex + semantic, cached, warm preload, modes).  
2. **Ruleset schema:** `src/directives_schema.json` (Enterprise E1.0) with hash anchored on-chain.  
3. **Output provenance:** `logs/output_log.jsonl` + `src/anchor_outputs.py` → Merkle root anchored on Sepolia.  
4. **Anchoring scripts:** `src/anchor_hash.py` (directives) and `src/anchor_outputs.py` (outputs).

---

## Roadmap Snapshot (See [ROADMAP.md](ROADMAP.md) for full details)

| Version                   | Key Milestone                                                                                | Target      |
| :------------------------ | :------------------------------------------------------------------------------------------- | :---------- |
| **v0.2 (2025)**           | Performance optimisation; caching; latency budget keys.                                     | Completed   |
| **v0.3 (Feb 2026)**       | Semantic guard (MiniLM), directive hash anchored, output Merkle anchoring, reviewer bundle. | Released    |
| **v0.4 (2026)**           | PoC stabilisation/pilot prep; CI, service/API hardening, proof/verify tooling.               | Planned     |
| **v1.0+**                 | Prompt-injection defence, service layer/GUI, tokenised incentives (post-v1).                | Planned     |

---

## How to Get Started & Contribute

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/jebus197/CANDELA.git](https://github.com/jebus197/CANDELA.git) 
    # Replace with your actual repo link
    cd CANDELA
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the PoC front door:**
    ```bash
    python3 run_guardian.py --help
    ```
    This supports local files (txt/md/pdf) and produces a reviewer-friendly JSON report.

We welcome contributions! See our `TECH_SPEC.md` for developer to-dos, `ROADMAP.md` for future plans, and the [Issues Tab](https://github.com/jebus197/CANDELA/issues) on GitHub. ---

*CANDELA – Illuminating AI governance through verifiable directives.*
*Copyright (c) 2024-2025 George Jackson (CANDELA Project Lead). MIT Licensed.*
