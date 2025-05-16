# CANDELA Project Roadmap

This document outlines the planned development phases for the CANDELA (Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring) project. Our goal is to move from the current Proof-of-Concept (PoC) to a robust, beta-ready system that enhances Large Language Model (LLM) reliability and transparency through verifiable, pre-execution rule anchoring.

This roadmap is a living document and will be updated as the project progresses, milestones are achieved, and community feedback is incorporated.

---

## Phase 0.1: Proof-of-Concept & Foundational Documentation (Target: Completed May 16, 2025)

**Objective:** Establish the core conceptual framework of CANDELA, demonstrate the basic technical feasibility of hashing the directive set, and create initial public-facing documentation.

* **[✓] Core Concept Definition:** LLM governance via a "Directive Guardian" middleware enforcing a pre-execution, blockchain-anchored "Directive Scaffold."
* **[✓] Initial Directive Set (v3.2):**
    * Developed `src/directives_schema.json` (76 directives).
    * Includes illustrative "micro-directive" decompositions for complex concepts like "Logical-Extension" (ID 6), "Associative Reasoning" (ID 14), and "First-Principles" (ID 24).
* **[✓] Guardian PoC Scripts:**
    * `src/guardian_poc_v0.1.py`: Primary PoC script demonstrating directive loading, SHA-256 hashing of the directive bundle, and a simulated Guardian workflow with mock LLM calls and blockchain anchoring.
    * Older illustrative scripts (`guardian_prototype.py`, `guardian_extended.py`) retained for reference.
* **[✓] Successful Directive Bundle Hash Generation:**
    * Verified SHA-256 hash for `directives_schema.json` v3.2: `3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa` (as documented in `README.md` and `First successful file hash.txt`).
* **[✓] Symbolic Manual Anchoring (PoC):** The v3.2 directive bundle hash has been manually recorded on a public testnet (details in `README.md`) to demonstrate the anchoring principle.
* **[✓] Initial Documentation Suite (v0.1):**
    * `README.md`: Main project overview.
    * `LICENSE`: MIT License established.
    * `TECH_SPEC.md`: Initial technical architecture and developer notes.
    * `docs/PROJECT_BRIEF.md`: Concise project summary.
    * `docs/FAQ.md`: Answers to common questions.
    * `docs/directives_README.md`: Guide to understanding the directive schema and micro-directives.
    * `docs/example_directives_schema_annotated.jsonc`: Commented schema for human readability.
* **[✓] GitHub Repository Established:** Public repository (`jebus197/CANDELA`) set up. * **[✓] OSF Preregistration & DOI:** Core documents registered on the Open Science Framework with a citable DOI. ---

## Phase 0.2: MVP - Core Guardian Functionality & Testnet Integration (Target: June - July 2025)

**Objective:** Develop a Minimum Viable Product (MVP) of the Guardian software that can interact with a live LLM, perform automated blockchain anchoring/verification of the directive set on a testnet, and execute basic "auto" tier directive validation.

* **Implement Real LLM API Integration:**
    * Modify `guardian_poc_v0.1.py` (or evolve into `guardian_mvp_v0.2.py`) to make actual API calls to a chosen LLM (e.g., OpenAI, Gemini).
    * Ensure secure API key management.
* **Implement Automated Testnet Blockchain Anchoring & Verification:**
    * Develop the Guardian module to programmatically anchor the `directive_bundle_hash` to a public testnet (e.g., Polygon Mumbai or Ethereum Sepolia via `web3.py`).
    * Implement the Guardian logic to retrieve this anchored hash and verify the integrity of the loaded `directives_schema.json` at runtime (as detailed in `TECH_SPEC.md` and Action Plan Task 2.1 from May 16th).
* **Implement Basic "Auto" Tier Validation Logic:**
    * Enhance the Guardian's `_validate_llm_output` function to perform actual checks for a selected subset of "auto" tier micro-directives (e.g., for IDs 6, 14, 24, 71-74) based on their `validation_criteria` in the schema.
* **Unit Testing Framework:**
    * Establish a basic unit testing framework (e.g., using `pytest`) for core Guardian functions, including directive loading, hashing, and the initial "auto" validation checks.
* **Refine `TECH_SPEC.md`:** Update with detailed MVP v0.2 specifications, including the blockchain verification protocol and defined "auto" tier validation targets.
* **Additional Feature ("AI Slop" Mitigation - Conceptual):**
    * “Must-include source” micro-directive & validator regex (extends IDs 30-32 from older `ROADMAP.md.txt` - to be formally integrated into schema if pursued for v0.2).

---

## Phase 0.3: Enhanced Validation, Empirical Testing & Initial Dissemination (Target: July - August 2025)

**Objective:** Expand the Guardian's validation capabilities, conduct initial empirical tests to measure Candela's impact, and begin academic dissemination.

* **Expand "Semi" Tier Validation (Heuristics):**
    * Research and implement more sophisticated heuristic-based checks for a selection of "semi" tier directives.
* **Semantic Linking of Directives (Proof-of-Concept):**
    * Explore and prototype mechanisms for the Guardian to recognize and leverage conceptual links between directives (e.g., First-Principles ⇄ Associative Reasoning ⇄ Logical Extension), as discussed for future versions in `directives_README.md`.
* **Content-Hash Footer (Conceptual - `ROADMAP.md.txt` v0.3):**
    * Design and prototype Guardian functionality to append a cryptographic hash of the final (validated) LLM output to the response, alongside the directive bundle hash, for enhanced I/O verifiability (New Directive 78 "Append HashFooter = true" from older `ROADMAP.md.txt` to be formally added to schema if pursued).
* **Conduct and Document Initial Empirical Tests:**
    * Design and run experiments with the MVP to measure:
        * LLM adherence to specific "auto" and initial "semi" tier directives.
        * Impact on hallucination rates or instruction following for defined tasks.
        * Performance overhead of the Guardian.
* **Draft arXiv Preprint / Technical Whitepaper:**
    * Document CANDELA's methodology, MVP architecture, blockchain verification protocol, and initial empirical findings.
* **CI/CD Pipeline:** Implement GitHub Actions for automated linting and unit testing.

---

## Phase 0.4: Guardian Extended Features & Early Pilots (Target: August - Q4 2025)

**Objective:** Add more sophisticated features to the Guardian and seek early pilot users or research collaborations.

* **Guardian Flags Low-Confidence Answers:** Implement robust mechanisms based on LLM-provided confidence scores or Guardian's own heuristics.
* **Search Engine Demo (Conceptual - `ROADMAP.md.txt` v0.4):** Develop a conceptual demo or whitepaper illustrating how search engines could use CANDELA's on-chain hashes to filter/rank content.
* **Prepare and Submit Workshop/Conference Paper(s):** Based on empirical results.
* **Targeted Outreach:** Engage with AI safety researchers, blockchain developers, and potential industry adopters based on MVP progress and empirical data.

---

## Phase 0.5: Public Beta & Community Building (Target: Q4 2025 - Q1 2026)

**Objective:** Release a more polished version of the Guardian for wider public testing and begin actively fostering a user and contributor community.

* **Public Beta Release:** Offer a user-friendly version of the Guardian (potentially as a library or simple application).
* **Browser Plug-in (Proof-of-Concept - `ROADMAP.md.txt` v0.5):** Develop a simple browser extension to query the CANDELA blockchain and visually indicate if web content is associated with a CANDELA-verified directive set.
* **Community Engagement:** Establish communication channels (e.g., Discord, forum) and actively solicit feedback and contributions.
* **Explore Creator Economy Integration (Initial PoC):**
    * Refine and prototype the "Creator Wallet" concept, allowing hashes of human-generated content (verified against community standards) to be linked to creator wallets on-chain.
    * Design initial smart contract concepts for tipping or basic revenue splits.

---

## Phase 1.0 and Beyond: Production, Ecosystem Growth & Standardization

**Objective:** Move towards a production-ready CANDELA system, foster a robust ecosystem, and explore broader applications and standardization.

* **Full Validator Suite:** Comprehensive validation logic for all applicable directives.
* **Mainnet Blockchain Anchoring:** Transition from testnet to a mainnet blockchain for production use cases, considering cost and scalability.
* **Integration with Existing Audit Platforms:** Explore APIs or partnerships to connect CANDELA's pre-execution verification with post-execution audit trail systems.
* **DAO for Governance:** Develop and implement a Decentralized Autonomous Organization for the governance of the CANDELA directive set and framework.
* **Standardization Efforts:** Work with relevant bodies and the community towards broader adoption and potential standardization of directive-driven AI governance and verifiable content principles.
* **Expand Media Types for Creator Economy:** Investigate extending the content verification and monetization framework beyond written media.

---

*This roadmap will be reviewed and updated quarterly, or as significant milestones are achieved.*
*Last Updated: May 16, 2025*