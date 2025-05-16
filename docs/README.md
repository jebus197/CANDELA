# CANDELA

**Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

*Illuminate AI behaviour through verifiable, pre-execution rule anchoring.*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/jebus197/CANDELA) [![MIT Licence](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

---

## The Challenge: Making AI Reliable and Transparent

Large Language Models (LLMs) are powerful tools, but they can be unpredictable. They might provide incorrect information ("hallucinate"), stray from initial instructions ("drift"), or offer inconsistent answers. Because their internal reasoning is often a "black box," it's hard to trust them for critical tasks or understand *why* they produce a specific output. This lack of reliability and transparency is a major hurdle for the safe and widespread use of AI.

**CANDELA addresses this by introducing the Directive Guardian: an external, verifiable system that guides and constrains LLM behaviour based on a publicly anchored set of rules.**

➡ **For a two-minute overview of the project, see our [Project Brief](docs/PROJECT_BRIEF.md).**
➡ **For answers to common questions, see our [FAQ](docs/FAQ.md).**

---

## How CANDELA Works: A Solution Overview

CANDELA uses a software component called the **"Directive Guardian"** that acts as a smart intermediary between a user (or an application) and any LLM. Here’s the core workflow:

1.  **Define the Rules (The "Directive Scaffold"):**
    * We start with a clear, human-readable set of rules called "directives." These tell the LLM how it should behave (e.g., be truthful, disclose uncertainty, follow specific reasoning steps).
    * These directives are stored in a machine-readable format (`src/directives_schema.json`).
    * For complex concepts like "first-principles reasoning," we break them down into smaller, testable "micro-directives." (Learn more in our [Guide to the Directive Schema](docs/directives_README.md)).

2.  **Secure the Rulebook (Blockchain Anchoring):**
    * Before any interaction, the Guardian takes a unique digital fingerprint (a SHA-256 hash) of the entire current directive set.
    * This **hash is recorded on a public blockchain testnet** (e.g., Polygon Mumbai or Ethereum Sepolia). This process is called "anchoring."
    * Because blockchain records are immutable (cannot be secretly changed), this anchored hash serves as a permanent, publicly verifiable proof of the exact rule-set that *should* be in force.

3.  **Verify Rule Integrity at Runtime:**
    * When the Guardian starts, it loads its local copy of the directives and calculates its hash.
    * It then queries the blockchain to retrieve the official anchored hash.
    * **If the local hash matches the blockchain hash, the Guardian knows its rules are authentic and untampered.** If they don't match, it signals an integrity issue.

4.  **Guide the LLM (Strategic Prompting):**
    * The Guardian intelligently incorporates the *verified* directives into the instructions (prompts) given to the LLM. This "nudges" the LLM to produce responses that align with the anchored rules.

5.  **Check the Work (Output Validation):**
    * After the LLM responds, the Guardian automatically checks the output against specific micro-directives using programmed logic (e.g., checking for required confidence tags, adherence to reasoning steps, word counts for specific micro-directive outputs).

6.  **Enforce and Log (Action Handling):**
    * If the output complies: It's passed to the user.
    * If it violates a rule: The Guardian can flag the issue, ask the LLM to try again (providing feedback on the violation), or prevent the non-compliant output from being shown.
    * For a complete audit trail, a fingerprint (hash) of the entire interaction (input, directives used, and final output) can also be anchored on the blockchain.

This system transforms a potentially unreliable LLM into a more predictable and accountable tool by wrapping it in a verifiable governance framework, ensuring that the rules of engagement are themselves transparent and secure.

---

## Key Features & Goals

* **Pre-Execution Rule Verification:** Ensures the integrity of behavioural rules *before* the LLM acts, using blockchain anchoring.
* **Micro-Directives:** Makes complex reasoning concepts (like "First-Principles" or "Associative Reasoning") operational and more easily testable through decomposition into smaller, concrete steps.
* **Transparency & Auditability:** Human-readable directives, a machine-parsable schema, and public blockchain records provide clear oversight into the AI's governance.
* **Enhanced Reliability:** Aims to reduce LLM hallucinations, drift, and inconsistencies by enforcing a stable rule-set.
* **Model-Agnostic Potential:** Designed as a middleware layer, CANDELA could theoretically be adapted to work with various LLMs.
* **Open Source:** The project is MIT licensed, encouraging community collaboration and broad adoption.
* **Future Vision – Combating "AI Slop" & Supporting Creators:** By enabling verifiable content (both AI and human-generated) against anchored standards, CANDELA could help identify quality information and potentially facilitate fairer recognition and revenue models for original content creators.

---

## Current Status (v0.1 Proof-of-Concept - May 2025)

* **Directive Set Defined:** Version 3.2 of the `directives_schema.json` includes 76 directives, with illustrative micro-directive breakdowns for "Logical-Extension" (ID 6), "Associative Reasoning" (ID 14), and "First-Principles" (ID 24).
* **Core Hashing Mechanism Demonstrated:** The `src/guardian_poc_v0.1.py` script successfully loads the directive schema, computes its SHA-256 hash, and simulates the core Guardian workflow with mock LLM calls and blockchain anchoring.
* **Documentation Suite:** Comprehensive documentation including this README, a [Project Brief](docs/PROJECT_BRIEF.md), [FAQ](docs/FAQ.md), [Technical Specification](TECH_SPEC.md), and a [Guide to the Directive Schema](docs/directives_README.md) are available.
* **Successful Symbolic Anchoring:** The hash of the v3.2 directive set has been successfully generated and documented below. A manual anchoring of this hash onto a public testnet has also been performed as a PoC step.

### Directive Bundle v3.2 Fingerprint (SHA-256 Hash)

This hash is the unique fingerprint of the `src/directives_schema.json` (Version 3.2) file. It allows anyone to verify they are working with the exact, canonical version of the CANDELA directive set.

* **Generated Hash:** `3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa`
    * *(As produced by `python3 src/guardian_poc_v0.1.py` on 2025-05-12, from `directives_schema.json` v3.2)*
* **Manually Anchored on Polygon Mumbai Testnet (PoC Step):**
    * **Date:** [Insert Date you performed manual anchoring, e.g., 2025-05-16]
    * **Transaction ID (TxID):** [Insert the TxID from your manual anchoring transaction here]
    * *(Note: Automated anchoring by the Guardian software is planned for MVP v0.2)*

Any change to the `src/directives_schema.json` file will result in a different hash. The `guardian_poc_v0.1.py` script can be used to re-calculate and verify this hash locally.

**Note on Schema Clarity:** For a human-friendly version of the directive schema with comments explaining the structure and micro-directive examples, please see [`docs/example_directives_schema_annotated.jsonc`](docs/example_directives_schema_annotated.jsonc). The actual runtime schema (`src/directives_schema.json`) must remain strict, comment-free JSON for reliable parsing by software.

---

## Repository Structure

| Path                               | Purpose                                                                    |
| :--------------------------------- | :------------------------------------------------------------------------- |
| `README.md`                        | This main project overview.                                                |
| `LICENSE`                          | The MIT License for the project.                                           |
| `TECH_SPEC.md`                     | Detailed technical architecture, workflow, and developer to-do list.       |
| `ROADMAP.md`                       | Planned development phases and future milestones.                          |
| `docs/`                            | Directory for human-readable documentation:                                |
| `docs/PROJECT_BRIEF.md`            | A concise 2-minute overview of CANDELA.                                    |
| `docs/FAQ.md`                      | Answers to Frequently Asked Questions.                                     |
| `docs/directives_README.md`        | Explains the structure of the directive schema and micro-directives.       |
| `docs/example_directives_schema_annotated.jsonc` | A commented version of the schema for easier human understanding. |
| `src/`                             | Directory for source code:                                                 |
| `src/directives_schema.json`       | The machine-readable directive list (v3.2, 76 items, strict JSON).       |
| `src/guardian_poc_v0.1.py`         | The primary, more comprehensive Proof-of-Concept script.                   |
| `src/guardian_prototype.py`        | An earlier, minimal PoC script (kept for reference/simplicity).          |
| `src/guardian_extended.py`         | An earlier, more commented PoC script (kept for reference).                |
| `requirements.txt`                 | Python dependencies for running the scripts.                               |
| `tests/`                           | (Placeholder for future unit tests for the Guardian software).             |

---

## Quick Start (Proof-of-Concept)

To run the current Proof-of-Concept and verify the directive bundle hash locally:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/jebus197/CANDELA.git](https://github.com/jebus197/CANDELA.git) 
    # Replace 'jebus197/CANDELA' with your actual repository path if different
    cd CANDELA
    ```

2.  **Install Dependencies** (currently only `requests` is listed, `web3.py` is commented out for future use):
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Main PoC Script:**
    ```bash
    python3 src/guardian_poc_v0.1.py
    ```
    The console output will show mock blockchain anchoring messages, the computed directive bundle hash, and a JSON summary of a simulated interaction. Compare the printed directive bundle hash with the one documented above to verify integrity.

---

## Roadmap Highlights

CANDELA is an evolving project. Key next steps include:

| Version | Milestone                                                              |
| :------ | :--------------------------------------------------------------------- |
| v0.2    | Implement real LLM API calls & automated Testnet anchoring for directives. |
| v0.3    | Develop the Guardian's "auto" tier validation logic for core directives. Establish a unit test suite. |
| v0.4+   | Expand validation capabilities, explore semantic linking, conduct empirical testing, and develop public beta. |

See the full [ROADMAP.md](ROADMAP.md) for more details.

---

## Contributing

CANDELA is an open-source project, and contributions are welcome! Please see the `TECH_SPEC.md` for areas needing development and the `ROADMAP.md` for longer-term goals.

1.  Fork the repository.
2.  Create a feature branch for your work.
3.  Ensure any code contributions adhere to basic Python best practices and are commented.
4.  If modifying directives, update `src/directives_schema.json`, regenerate the bundle hash, and document the version change.
5.  Submit a Pull Request with a clear description of your changes.
6.  Check the [Issues Tab](https://github.com/jebus197/CANDELA/issues) for current tasks or to report bugs. ---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

*CANDELA – Illuminating AI governance through verifiable directives.*