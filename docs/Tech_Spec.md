# CANDELA – Technical Specification (v0.3 - Feb 2026)

**CANDELA: Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

**Purpose:**
This document details the technical architecture, workflow, and implementation plan for the **CANDELA "Directive Guardian"** middleware. The Guardian is designed to enforce a machine-readable set of behavioral rules ("directives") on any Large Language Model (LLM). It achieves this by loading a verified directive set (whose integrity is confirmed against a blockchain-anchored hash), integrating directives into LLM prompts, validating LLM outputs against these rules, and using blockchain technology to optionally anchor hashes of interaction logs for immutability and provenance.

---

## 1. High-Level Architecture

The CANDELA system operates with the Directive Guardian as a central middleware component:

**User/Application → Directive Guardian Middleware → LLM API → Directive Guardian Validator → (Optional) Blockchain Anchor for I/O**

The key stages within the Guardian are:

1.  **Guardian Loader & Integrity Verification:**
    * Loads the `src/directives_schema.json` file.
    * Computes its SHA-256 hash.
    * (MVP Goal) Queries a designated blockchain (e.g., Polygon Mumbai testnet) to retrieve the canonical anchored hash of the current official directive set.
    * Compares the local hash with the blockchain hash. If mismatched, an integrity alert is raised, and operation with unverified directives is prevented.
2.  **Prompt Builder:**
    * Strategically prepends or integrates the (now verified) directives, or a relevant subset (especially micro-directives), into the user's prompt before sending it to the LLM.
3.  **LLM Caller:**
    * Securely sends the composed prompt to an external LLM API (e.g., OpenAI, Gemini, Anthropic).
4.  **Output Validator:**
    * Receives the LLM's raw response.
    * Programmatically checks this response against the `validation_criteria` defined for applicable directives in the `directives_schema.json` (focusing on "auto" tier directives in early versions).
    * Identifies and logs any compliance failures.
5.  **Action Handler & (Optional) I/O Anchoring:**
    * If validated, the response is passed to the user/application.
    * If validation fails, the Guardian can initiate retries (with feedback to the LLM), flag errors, or block the response.
    * Optionally, a hash of the complete interaction bundle (input, verified directives used, final LLM response, validation status) can be anchored on the blockchain for a full audit trail.

---

## 2. Repository Structure (Current PoC v0.3)

| Path                                               | Purpose                                                                                       |
| :------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| `README.md`                                        | Main project overview, status, quick start, and links to other docs.                            |
| `LICENSE`                                          | MIT License for the project.                                                                  |
| `TECH_SPEC.md`                                     | *This document:* Detailed technical architecture, workflow, and developer to-do list.         |
| `ROADMAP.md`                                       | Planned development phases and future milestones.                                             |
| `docs/`                                            | Directory for human-readable documentation guides:                                            |
| `docs/PROJECT_BRIEF.md`                            | A concise 2-minute overview of CANDELA.                                                       |
| `docs/FAQ.md`                                      | Answers to Frequently Asked Questions.                                                        |
| `docs/directives_README.md`                        | Explains the structure of the directive schema and the micro-directive strategy.                |
| `docs/example_directives_schema_annotated.jsonc`   | A commented version of the schema with headings for easier human understanding (not for runtime). |
| `src/`                                             | Directory for source code:                                                                    |
| `src/directives_schema.json`                       | The machine-readable directive list (v3.2, 76 items, strict JSON format).                     |
| `src/guardian_prototype.py`                        | Core PoC Guardian (hashing, anchoring, basic checks).                                         |
| `src/guardian_extended.py`                         | Regex guard + lazy hand-off to prototype.                                                    |
| `src/guardian_runtime.py`                          | Cached runtime wrapper + async Mini‑BERT hook + output logging.                              |
| `logs/output_log.jsonl`                            | Append-only log of every checked output (input hash, verdict, timestamp).                    |
| `src/anchor_outputs.py`                            | Batches output log into a Merkle root and anchors it on-chain.                               |
| `requirements.txt`                                 | Canonical dependencies (includes sentence-transformers).                                      |
| `tests/`                                           | Active tests (`test_regex_guard.py`, `test_directive_schema.py`).                             |
| `CITATION.cff`                                     | Present in repo root.                                                                         |

---

## 3. Dependencies & Setup (for PoC `guardian_prototype.py` + `guardian_runtime.py`)

* **Python:** Version 3.8+ recommended.
* **Libraries:**
    * `requests`: For making HTTP calls to LLM APIs (when real integration is implemented).
    * `web3.py` (Optional for PoC, required for MVP blockchain interaction): For interacting with Ethereum-compatible blockchains like Polygon. Install via `pip install web3`.
* **Setup:**
    ```bash
    git clone [https://github.com/jebus197/CANDELA.git](https://github.com/jebus197/CANDELA.git) 
    # Replace with your actual repo link
    cd CANDELA
    pip install -r requirements.txt
    ```
* **Environment Variables (for future MVP development):**
    * `YOUR_LLM_API_KEY_ENV_VARIABLE`: For the chosen LLM provider.
    * `YOUR_BLOCKCHAIN_RPC_URL_ENV_VARIABLE`: RPC endpoint for the chosen testnet (e.g., Polygon Mumbai: `https://rpc-mumbai.maticvigil.com`, or Ethereum Sepolia).
    * `ANCHOR_PRIVATE_KEY_ENV_VARIABLE`: Private key of the wallet used for anchoring transactions on the testnet (ensure this wallet is funded with testnet tokens).

---

## 4. Guardian Workflow (Implemented in `guardian_prototype.py`)

| Step                                     | Function in `guardian_prototype.py` | PoC Status / Notes                                                                                                                               |
| :--------------------------------------- | :--------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Load Directives & Compute Local Hash  | `_load_and_hash_directives()`      | Loads `src/directives_schema.json`, computes SHA-256. Includes basic error handling.                                                            |
| 2. Verify Directive Set Integrity        | `_verify_directive_set_integrity()`| **CRITICAL STUB.** Currently simulates success if directives load. MVP: Must query blockchain for canonical hash & compare.                     |
| 3. Anchor Verified Directive Bundle Hash | `_anchor_to_blockchain()`          | **MOCK.** Simulates anchoring `self.directive_bundle_hash`. MVP: Implement real testnet transaction.                                             |
| 4. Construct LLM Prompt                  | `_construct_llm_prompt()`          | Prepends core directives (e.g., IDs 1-3) to user input. MVP: Needs more sophisticated directive selection & token management.                      |
| 5. Call LLM API                          | `_call_llm_api()`                  | **MOCK.** Simulates LLM call, returns cycling responses. MVP: Implement real HTTP POST to LLM API.                                                 |
| 6. Validate LLM Output                   | `_validate_llm_output()`           | **VERY BASIC POC.** Illustrative checks for "Confidence:" tag and one micro-directive structure. MVP: Implement checks for all "auto" tier directives. |
| 7. Retry Loop for Validation             | Loop in `process_user_request()`   | Basic retry if validation issues found. MVP: Refine regeneration prompt.                                                                         |
| 8. Anchor I/O Bundle Hash                | `_anchor_to_blockchain()`          | **MOCK.** Simulates anchoring hash of (prompt, response, issues, directive_hash). MVP: Implement real testnet transaction for audit trail.         |

---

## 5. Directive Validation Overview (Phased Approach)

Compliance with directives will be validated in tiers, as detailed in `docs/directives_README.md`:

* **"auto" tier:** Rules with clear, objective `validation_criteria` (e.g., regex, word counts, presence of specific keywords/structures for micro-directives). Implementation of these is the focus for the early MVP (v0.2/v0.3).
* **"semi" tier:** Rules requiring more complex heuristics or lightweight NLP models. Planned for later MVP stages.
* **"human" tier:** Inherently subjective or highly nuanced ethical rules that will likely always require human oversight or integration with external policy engines. The Guardian may flag these for review.

The `src/directives_schema.json` file includes a `validation_criteria` field for each directive, guiding the implementation of these checks.

---

## 6. Blockchain Anchoring Details (Target: Polygon Mumbai or Ethereum Sepolia Testnet for MVP)

* **What is Anchored:**
    1.  The SHA-256 hash of the canonical `directives_schema.json` file.
    2.  (Optionally for MVP, more robustly in later versions) The SHA-256 hash of an "I/O Bundle" (containing user input, relevant directives applied, final LLM response, and validation status) for each significant interaction.
* **Mechanism (Contract-less for Simplicity in MVP):**
    * Each hash will be embedded in the `data` field of a zero-value transaction sent on the chosen testnet.
    * This creates a publicly verifiable, timestamped record without the need to deploy and maintain a custom smart contract initially.
* **Verification:** The Guardian will query the blockchain (via an RPC URL) for the latest anchored directive hash to compare against its local version.
* **Tools:** `web3.py` library for Python interaction with Ethereum-compatible chains.

---

## 7. Developer To-Do List (Towards MVP v0.3 - v0.4)

1.  **Real LLM Integration (High Priority):**
    * Implement the `_call_llm_api()` function in a dedicated `guardian_mvp.py` to make live calls to a chosen LLM API (e.g., OpenAI).
    * Implement secure API key management (using environment variables).
    * Implement robust error handling for API calls.
2.  **Implement Directive Set Integrity Verification (High Priority):**
    * Fully implement `_verify_directive_set_integrity()` to query the chosen testnet for the canonical directive bundle hash and compare it with the locally computed hash. Define clear actions for match/mismatch.
3.  **Implement Automated Blockchain Anchoring (High Priority):**
    * Fully implement `_anchor_to_blockchain()` to programmatically write:
        * The verified `directive_bundle_hash` to the testnet.
        * The `io_bundle_hash` to the testnet.
4.  **Expand Validation Logic (Medium Priority for MVP Core):**
    * Begin implementing the "auto" tier validation checks in `_validate_llm_output()` based on the `validation_criteria` in `directives_schema.json` for key micro-directives (e.g., IDs 6a-c, 14a-c, 24a-c) and critical monitoring directives (e.g., IDs 71-74).
5.  **Unit Testing Framework (Medium Priority):**
    * Set up `pytest` in the `tests/` folder.
    * Write initial unit tests for: directive loading/hashing, core "auto" validation logic, and mock interactions for the blockchain functions.
6.  **Refine Prompt Engineering (Medium Priority):**
    * Experiment with different ways to structure and include directives in the LLM prompt for optimal adherence within token limits.
7.  **Documentation Updates (Ongoing):**
    * Add an architecture diagram (e.g., PNG) to the `docs/` folder and reference it.
    * Update this `TECH_SPEC.md` and other documents as MVP features are implemented.
    * Add `CITATION.cff` file to the repository root.

---

## 8. Versioning & Anchoring Policy

| Event                                     | Version Bump Example | Action Required                                                                     |
| :---------------------------------------- | :------------------- | :---------------------------------------------------------------------------------- |
| Change to directive text, ID, or criteria | v0.3.x → v0.4.0      | Recompute directive bundle hash, anchor new hash on blockchain, update all docs.      |
| Guardian code refactor (no directive change) | v0.3.0 → v0.3.1      | No re-anchoring of directive hash needed. Update software version.                   |
| New directive added to schema             | v0.3.x → v0.4.0      | Update schema, tests, docs. Recompute bundle hash, anchor new hash.                 |
| Breaking change to schema structure       | v0.x.x → v1.0.0      | Migrate validation harness, update all docs. Recompute bundle hash, anchor new hash. |

*(This policy ensures that there's always a clear link between a software version, the directive set version it uses, and its corresponding on-chain anchored hash.)*

---

## 9. Security Considerations (Initial)

* **API Key Management:** LLM API keys and blockchain private keys must be stored securely (e.g., environment variables, secrets management tools), never hardcoded.
* **Blockchain Private Key Security:** The private key for the anchoring wallet must be kept secure. For PoC/MVP on testnet, risk is low, but good practices are essential.
* **Prompt Injection:** While directives aim to constrain output, sophisticated prompt injection techniques against the LLM itself remain a general concern. The Guardian's output validation is a layer of defense.
* **Data Privacy:** Ensure no sensitive user data is inadvertently included in hashes or logs anchored on a public blockchain. Hash only non-sensitive metadata or content fingerprints.

---

## 10. Governance Roadmap (Conceptual)

1.  **Phase 1 (Current):** Maintainer-led (George Jackson).
2.  **Phase 2 (Post-MVP):** Form a small community advisory group.
3.  **Phase 3 (Longer-Term):** Explore a Decentralized Autonomous Organization (DAO) model for governing the canonical directive set and the CANDELA framework itself.

---

*This Technical Specification is a living document and will be updated as the CANDELA project evolves.*
*Last Updated: May 16, 2025*
*Repository: [https://github.com/jebus197/CANDELA](https://github.com/jebus197/CANDELA)* *Copyright (c) 2024-2025 George Jackson (CANDELA Project Lead). MIT Licensed.*
