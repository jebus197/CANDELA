# CANDELA

**Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

*Illuminate AI behaviour through verifiable, pre-execution rule anchoring.*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/jebus197/CANDELA) [![MIT Licence](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
[![CANDELA Project Brief](https://img.shields.io/badge/Project%20Brief-View%20on%20OSF-blue.svg)](YOUR_OSF_PROJECT_LINK_HERE) ---

## The Challenge: Making AI Reliable and Transparent

Large Language Models (LLMs) are powerful tools, but they can be unpredictable. [cite: 2] They might provide incorrect information ("hallucinate"), stray from initial instructions ("drift"), or offer inconsistent answers. [cite: 2, 3] Because their internal reasoning is often a "black box," it's hard to trust them for critical tasks or understand *why* they produce a specific output. [cite: 3, 4] This lack of reliability and transparency is a major hurdle for the safe and widespread use of AI. [cite: 4, 5] **CANDELA addresses this by introducing the Directive Guardian: an external, verifiable system that guides and constrains LLM behaviour based on a publicly anchored set of rules.** [cite: 5]

➡ **For a two-minute overview of the project, see our [Project Brief](docs/PROJECT_BRIEF.md).**
➡ **For answers to common questions, see our [FAQ](docs/FAQ.md).**

---

## How CANDELA Works: A Solution Overview

CANDELA uses a software component called the **"Directive Guardian"** (envisioned as middleware) that acts as a smart intermediary between a user (or an application) and any LLM. [cite: 6] Here’s the core workflow:

1.  **Define the Rules (The "Directive Scaffold"):**
    * We start with a clear, human-readable set of rules called "directives." [cite: 7] These tell the LLM how it should behave (e.g., be truthful, disclose uncertainty, follow specific reasoning steps). [cite: 7, 8] * These directives are stored in a machine-readable JSON format (`src/directives_schema.json`). [cite: 8, 9] * For complex conceptual directives (like "first-principles reasoning" or "associative reasoning"), CANDELA employs a "micro-directive" strategy. [cite: 9, 10] This breaks down abstract concepts into smaller, concrete, and more easily testable steps. [cite: 10, 11] (Learn more in our [Guide to the Directive Schema](docs/directives_README.md)). [cite: 11]

2.  **Secure the Rulebook (Blockchain Anchoring):**
    * Before any interaction, the Guardian takes a unique digital fingerprint (a SHA-256 hash) of the entire current directive set (from `src/directives_schema.json`). [cite: 12] * This **hash is recorded on a public blockchain testnet** (e.g., Polygon Mumbai or Ethereum Sepolia are planned targets). [cite: 12, 13] This process is called "anchoring."
    * Because blockchain records are immutable (cannot be secretly changed without detection), this anchored hash serves as a permanent, publicly verifiable proof of the exact rule-set that *should* be in force at a given time. [cite: 13, 14] 3.  **Verify Rule Integrity at Runtime:**
    * When the Guardian system starts a session, it loads its local copy of the directives (`src/directives_schema.json`) and calculates its SHA-256 hash. [cite: 14, 15] * It then (in a full MVP implementation) queries the blockchain to retrieve the official, anchored hash for the canonical directive set. [cite: 15, 16] * **If the local hash matches the blockchain hash, the Guardian confirms that its local rules are authentic and untampered.** If they don't match, it signals an integrity issue, preventing operation with potentially compromised rules. [cite: 16, 17] 4.  **Guide the LLM (Strategic Prompting):**
    * The Guardian intelligently incorporates the *verified* directives (or a relevant subset) into the instructions (prompts) given to the LLM. [cite: 17, 18] This "nudges" the LLM to produce responses that align with the anchored rules. [cite: 18, 19] 5.  **Check the Work (Output Validation):**
    * After the LLM responds, the Guardian automatically checks the LLM's output against the specific micro-directives and other applicable rules. [cite: 19, 20] This involves programmed logic (e.g., checking for required confidence tags, adherence to reasoning steps defined in micro-directives, word counts for specific outputs, etc.). [cite: 20, 21] 6.  **Enforce and Log (Action Handling):**
    * **If compliant:** The LLM's output is passed to the user. [cite: 21, 22] * **If it violates a rule:** The Guardian can flag the specific issue, ask the LLM to regenerate the response (potentially with feedback on the violation), or prevent the non-compliant output from being shown. [cite: 22, 23] * **Auditable Record:** For a complete audit trail, a fingerprint (hash) of the entire interaction (user input, directives applied, and the final validated LLM output) can also be optionally anchored on the blockchain. [cite: 23, 24] This system transforms a potentially unreliable LLM into a more predictable, transparent, and accountable tool by wrapping it in a verifiable governance framework. [cite: 24, 25] The key is that the rules of engagement are themselves transparently defined and their integrity is secured. [cite: 25, 26] ---

## Directive Bundle Integrity: The Role of the Hash

A core principle of CANDELA is ensuring that the set of rules (directives) governing the AI's behavior is exactly what it's intended to be, without any undetected modifications. [cite: 26, 27] This is achieved through cryptographic hashing.

* **What is a Hash?** A hash function takes an input (like our entire `directives_schema.json` file) and produces a fixed-size string of characters (the hash). [cite: 27, 28] This hash is like a unique digital fingerprint. Even a tiny change in the input file will result in a completely different hash. [cite: 28, 29] * **Our Directive Bundle Hash (v3.2):**
    * **SHA-256 Hash:** `3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa`
    * *This hash was generated by running `python3 src/guardian_poc_v0.1.py` (which internally uses `guardian_prototype.py`'s hashing logic for now) on the `src/directives_schema.json` (Version 3.2) file on 2025-05-12, as per `First successful file hash.txt`.*
* **Purpose & Significance:**
    1.  **Integrity Verification:** This hash serves as the definitive fingerprint of the v3.2 directive set. [cite: 29, 30] The Guardian software (in its MVP stage) will compare the hash of its local directive file against a canonical version of this hash retrieved from the blockchain. [cite: 30, 31] A match confirms the local rules are authentic and untampered. [cite: 31, 32] 2.  **Transparency:** Anyone can independently take the `src/directives_schema.json` file from this repository, calculate its SHA-256 hash, and verify that it matches the hash documented here and (once implemented) anchored on the blockchain. [cite: 32, 33] 3.  **Auditability:** When an LLM interaction is logged with this directive bundle hash, it creates a verifiable link between the AI's output and the exact set of rules that were supposed to govern its behavior. [cite: 33, 34] * **Manual PoC Anchoring (Illustrative):**
    * **Testnet:** Polygon Mumbai Testnet
    * **Date:** [Insert Date you performed manual anchoring, e.g., 2025-05-16]
    * **Transaction ID (TxID):** [Insert the TxID from your manual anchoring transaction here]
    * *(Note: This manual step demonstrates the concept. Automated on-chain anchoring and verification by the Guardian software are key features planned for CANDELA's Minimum Viable Product - MVP v0.2/v0.3 as per our `ROADMAP.md`)*

**Note on Schema Readability:** For a version of the directive schema with comments explaining the structure and micro-directive examples (intended for human review), 
[cite: 35] please see [`docs/example_directives_schema_annotated.jsonc`](docs/example_directives_schema_annotated.jsonc). The actual runtime schema used by the Guardian (`src/directives_schema.json`) must remain strict, comment-free JSON for reliable software parsing. [cite: 35, 36] ---

## Key Features & Goals of CANDELA

* **Pre-Execution Rule Verification:** Ensures the integrity of behavioural rules *before* the LLM acts, using blockchain anchoring of the directive set's hash. [cite: 36, 37] * **Micro-Directives:** Makes complex reasoning concepts (like "First-Principles" or "Associative Reasoning") operational and more easily testable through decomposition into smaller, concrete steps. [cite: 37, 38] * **Transparency & Auditability:** Human-readable directives, a machine-parsable schema, and public blockchain records provide clear oversight into the AI's governance. [cite: 38, 39] * **Enhanced Reliability:** Aims to reduce LLM hallucinations, drift, and inconsistencies by enforcing a stable, verified rule-set. [cite: 39, 40] * **Model-Agnostic Potential:** Designed as a middleware layer, CANDELA could theoretically be adapted to work with various LLMs. [cite: 40, 41] * **Open Source:** The project is MIT licensed, encouraging community collaboration and broad adoption. [cite: 41, 42] * **Future Vision – Combating "AI Slop" & Supporting Content Creators:** By enabling verifiable content (both AI and human-generated) against anchored standards, CANDELA could help identify quality information and potentially facilitate fairer recognition and revenue models for original content creators. [cite: 42, 43] ---

## Repository Structure

| Path                                       | [cite: 44] Purpose                                                                    |
| :----------------------------------------- | :------------------------------------------------------------------------- |
| `README.md`                                | [cite: 46] This main project overview.                                                |
| `LICENSE`                                  | [cite: 47] The MIT License for the project.                                           |
| `TECH_SPEC.md`                             | [cite: 48] Detailed technical architecture, workflow, and developer to-do list.       |
| `ROADMAP.md`                               | [cite: 50] Planned development phases and future milestones.                          |
| `docs/`                                    | [cite: 51] Directory for human-readable documentation:                                |
| `docs/PROJECT_BRIEF.md`                    | [cite: 53] A concise 2-minute overview of CANDELA.                                    |
| `docs/FAQ.md`                              | [cite: 54] Answers to Frequently Asked Questions.                                     |
| `docs/directives_README.md`                | [cite: 55] Explains the structure of the directive schema and micro-directives.       |
| `docs/example_directives_schema_annotated.jsonc` | [cite: 56] A commented version of the schema for easier human understanding. |
| `src/`                                     | [cite: 58] Directory for source code:                                                 |
| `src/directives_schema.json`               | [cite: 60] The machine-readable directive list (v3.2, 76 items, strict JSON).       |
| `src/guardian_poc_v0.1.py`                 | [cite: 62] The primary, more comprehensive Proof-of-Concept script.                   |
| `src/guardian_prototype.py`                | [cite: 63] An earlier, minimal PoC script (illustrative).                             |
| `src/guardian_extended.py`                 | [cite: 64] An earlier, more commented PoC script (illustrative).                      |
| `requirements.txt`                         | [cite: 65] Python dependencies for running the scripts.                               |
| `tests/`                                   | [cite: 66] (Placeholder for future unit tests for the Guardian software).             |
[cite: 67] ---

## Quick Start (Proof-of-Concept v0.1)

To run the current Proof-of-Concept and verify the directive bundle hash locally:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/jebus197/CANDELA.git](https://github.com/jebus197/CANDELA.git) 
    # Ensure this is your correct repository path
    cd CANDELA
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt 
    # (Currently includes 'requests'; 'web3.py' is commented out for future MVP)
    ```

3.  **Run the Main PoC Script:**
    ```bash
    python3 src/guardian_poc_v0.1.py
  
[cite: 68]   ```
    The console output will show mock blockchain anchoring messages, the computed **directive bundle hash** (compare this with the one documented above), and a JSON summary of a simulated LLM interaction.
[cite: 69] ---

## Roadmap Highlights

CANDELA is an evolving project. Key next steps include:

| Version | [cite: 70] Milestone                                                              |
| :------ | :--------------------------------------------------------------------- |
| v0.2    | [cite: 72] Implement real LLM API calls & automated Testnet anchoring for directives by the Guardian software. |
| v0.3    | [cite: 73] Develop the Guardian's "auto" tier validation logic for core directives. [cite: 74] Establish an initial unit test suite. |
| v0.4+   | [cite: 75] Expand validation capabilities, explore semantic linking of directives, conduct empirical testing, and develop towards a public beta. |
[cite: 76] See the full [ROADMAP.md](ROADMAP.md) for more details.

---

## Contributing

CANDELA is an open-source project, and contributions are welcome! [cite: 77] Please see the `TECH_SPEC.md` for areas needing development and the `ROADMAP.md` for longer-term goals.

1.  Fork the repository. [cite: 78] 2.  Create a feature branch for your work.
3.  Ensure any code contributions adhere to basic Python best practices and are clearly commented. [cite: 79] 4.  If modifying directives, please update `src/directives_schema.json`, regenerate the bundle hash (and document it), and clearly note the version change. [cite: 80] 5.  Submit a Pull Request with a clear description of your changes. [cite: 81] 6.  Check the [Issues Tab](https://github.com/jebus197/CANDELA/issues) on GitHub for current tasks or to report bugs. [cite: 81, 82] ---

## How to Cite CANDELA

If you use CANDELA in your research or project, please cite it. [cite: 82, 83] You can use the OSF DOI:
* [YOUR_OSF_PROJECT_DOI_LINK_HERE] (A `CITATION.cff` file may be added in the future for easier academic citation). [cite: 83, 84] ---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details. [cite: 84, 85] Copyright (c) 2024-2025 George Jackson (CANDELA Project Lead) ---

*CANDELA – Illuminating AI governance through verifiable directives.*
