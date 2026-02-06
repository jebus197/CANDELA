# CANDELA – Project Brief (v0.1.1 - May 2025)

**CANDELA: Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

## Elevator Pitch

**CANDELA adds a blockchain-anchored "Directive Guardian" layer in front of any Large Language Model (LLM). It transforms often fragile LLM prompt rules and behavioral guidelines into a verifiable and auditable governance system.**

---

## The Problem: Unreliable & Opaque AI

Current Large Language Models (LLMs), while incredibly powerful, often exhibit unpredictable behavior. They can produce incorrect information ("hallucinate"), deviate from instructions ("drift"), and their internal decision-making processes are largely opaque ("black boxes"). This lack of inherent reliability and transparency poses significant risks, limiting their trustworthiness for critical applications and making true accountability difficult to achieve.

## CANDELA's Solution: Verifiable Pre-Execution Governance

CANDELA introduces the **"Directive Guardian,"** a middleware software component designed to sit between a user (or application) and an LLM. The Guardian enforces a predefined, human-readable set of behavioral and cognitive rules called the **"Directive Scaffold."**

The core principles are:

1.  **Defined Rule-Set:** The Directive Scaffold (currently 76 directives, including examples of "micro-directives" for complex concepts) is stored in a machine-readable JSON format (`src/directives_schema.json`).
2.  **Integrity via Blockchain Anchoring:** Before the Guardian uses these directives, it calculates a unique cryptographic fingerprint (SHA-256 hash) of the entire directive set. This hash is then recorded ("anchored") on a public blockchain testnet (e.g., Polygon Mumbai or Ethereum Sepolia). This creates an immutable, publicly verifiable record of the exact rule-set that *should* be in force.
3.  **Runtime Verification:** At the start of an interaction, the Guardian verifies the integrity of its local directive set by comparing its hash against the canonical hash retrieved from the blockchain.
4.  **Guided LLM Output:** The Guardian strategically incorporates the verified directives into prompts sent to the LLM.
5.  **Automated Validation:** The Guardian checks the LLM's responses against the requirements of the active directives (especially "auto" tier micro-directives in the current PoC).
6.  **Accountability Loop:** The system enables an auditable trail from the enforced rules to the LLM's behavior, with options to also anchor hashes of interactions.

---

## Key Innovations & Benefits

* **Pre-Execution Rule Verification:** Ensures the governing rule-set's integrity *before* the LLM generates output.
* **Micro-Directives:** Decomposes complex abstract concepts (like "First-Principles Reasoning") into smaller, concrete, and more easily testable steps for the LLM and Guardian.
* **Transparency & Auditability:** Human-readable directives coupled with blockchain-anchored verification provide unprecedented oversight.
* **Enhanced LLM Reliability:** Aims to reduce hallucinations, instructional drift, and inconsistencies.
* **Open & Model-Agnostic Potential:** Designed as an open-source (MIT licensed) middleware layer.
* **Addressing "AI Slop" & Supporting Content Creators (Future Vision):** The framework's principles could be extended to verify human-generated content against defined standards, potentially combating low-quality "AI slop" and enabling fairer monetization for original creators.

---

## Current Status (v0.3 — Feb 2026)

* **Guardian:** `src/guardian_runtime.py` provides regex + Mini‑BERT semantic checks with caching; every checked output is logged for audit.
* **Directive set:** `src/directives_schema.json` (v3.2, 76 directives) — canonical SHA-256 `7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d`.
* **Anchoring:**  
  * Directive bundle hash anchored on Sepolia (`docs/ANCHORS.md`).  
  * Output log batches anchored via Merkle roots using `src/anchor_outputs.py`.
* **Docs/DOI:** OSF DOI 10.17605/OSF.IO/3S7BT; Tech Spec/README/Roadmap synced to v0.3; reviewer bundle available.

## Key Components (v0.3)

1. **Guardian runtime:** `src/guardian_runtime.py` (regex + semantic, cached) calling `guardian_extended.py`/Mini‑BERT detector.
2. **Directive schema:** `src/directives_schema.json` (v3.2) with hash anchored on-chain.
3. **Output provenance:** `logs/output_log.jsonl` + `src/anchor_outputs.py` → Merkle root anchored on Sepolia.
4. **Anchoring scripts:** `src/anchor_hash.py` (directives) and `src/anchor_outputs.py` (outputs).

---

## Roadmap Snapshot (See [ROADMAP.md](ROADMAP.md) for full details)

| Version                   | Key Milestone                                                                                | Target      |
| :------------------------ | :------------------------------------------------------------------------------------------- | :---------- |
| **v0.2 (2025)**           | Performance optimisation; caching; latency budget keys.                                     | Completed   |
| **v0.3 (Feb 2026)**       | Semantic guard (Mini‑BERT), directive hash anchored, output Merkle anchoring, reviewer bundle. | Released    |
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
3.  **Run the Proof-of-Concept:**
    ```bash
    python3 src/guardian_poc_v0.1.py
    ```
    This will demonstrate the directive loading, hashing, and mock interaction flow.

We welcome contributions! See our `TECH_SPEC.md` for developer to-dos, `ROADMAP.md` for future plans, and the [Issues Tab](https://github.com/jebus197/CANDELA/issues) on GitHub. ---

*CANDELA – Illuminating AI governance through verifiable directives.*
*Copyright (c) 2024-2025 George Jackson (CANDELA Project Lead). MIT Licensed.*
