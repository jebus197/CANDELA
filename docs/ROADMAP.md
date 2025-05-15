# CANDELA Project Roadmap

This document outlines the planned development phases for the CANDELA project. Our goal is to move from the current Proof-of-Concept to a robust, beta-ready system.

## Phase 0.1: Proof-of-Concept (Completed May 2025)

* [✓] **Core Concept Definition:** LLM governance via pre-execution, blockchain-anchored directive scaffold.
* [✓] **Initial Directive Set:** Developed and structured into `directives_schema.json` (v3.2, 76 directives including micro-directive examples).
* [✓] **Guardian Prototype:**
    * `guardian_prototype.py`: Loads directives, computes SHA-256 hash, simulates LLM call and validation, simulates blockchain anchoring.
    * `guardian_extended.py`: Provides a more detailed illustrative workflow with error handling and stubs for real LLM/blockchain calls.
* [✓] **Basic Hashing Loop:** Successfully demonstrated `src/guardian_prototype.py` generating consistent hashes for the directive bundle and mock I/O.
* [✓] **Initial Documentation:** README, FAQ, Project Brief, Technical Specification, and Directive Schema Guide created.
* [✓] **GitHub Repository:** Public repository established with MIT License.

## Phase 0.2: MVP - Validation Tiers & Testnet Anchoring (Target: June - July 2025)

* **Implement Validation Tiers:**
    * Enhance `guardian_extended.py` to parse `validation_tier` ("auto", "semi", "human") from `directives_schema.json`.
    * Implement actual validation logic for all "auto" tier directives (regex, keyword checks, structural checks for micro-directives like 6a-c, 14a-c, 24a-c, 71-74).
    * For "semi" and "human" tiers, the Guardian will log that these directives apply but that automated validation is pending or requires human review.
* **Real LLM Integration:**
    * Integrate `guardian_extended.py` with a live LLM API (e.g., OpenAI, Gemini), ensuring API keys are handled securely (environment variables).
* **Testnet Blockchain Anchoring:**
    * Implement actual blockchain anchoring for the directive bundle hash using `web3.py` (or similar) to a public testnet (e.g., Ethereum Sepolia, Polygon Mumbai).
    * The `TECH_SPEC.md` provides a sample `anchor_hash` function.
* **Unit Testing Framework:**
    * Set up `pytest` (or similar) in the `tests/` directory.
    * Write initial unit tests for:
        * Directive loading and hash integrity.
        * Core "auto" validation checks.
* **Documentation Update:**
    * Reflect implemented validation tiers and real anchoring in all relevant documents.
    * Update `directives_schema.json` if more directives are moved to "auto" with defined `validation_criteria`.

## Phase 0.3: Enhanced Validation & Semantic Linking (Target: July - August 2025)

* **Expand "Semi" Tier Validation:**
    * Research and implement more sophisticated heuristics or lightweight NLP models for some "semi" tier directives (e.g., basic sentiment, more nuanced uncertainty detection).
* **Semantic Linking (Proof-of-Concept):**
    * As outlined in `directives_README.md`, explore and prototype mechanisms for linking related complex directives (e.g., First-Principles ⇄ Associative Reasoning ⇄ Logical Extension). This might involve tracking concepts across micro-directive steps.
* **Content-Hash Footer:**
    * Implement Directive 78 (placeholder): Guardian appends a cryptographic hash of the final (validated) LLM output to the response, alongside the directive bundle hash. This creates a verifiable link between the rules, the input, and the specific output.
* **CI/CD Pipeline:**
    * Set up GitHub Actions for automated linting and unit testing on pull requests.

## Phase 0.4: Guardian Extended Features & Early Pilots (Target: August - Q4 2025)

* **Guardian Flags Low-Confidence Answers:** Implement robust mechanisms based on LLM-provided confidence scores or Guardian's own heuristics to flag or handle low-confidence outputs more effectively.
* **"Must-Include Source" Micro-Directive:** Fully implement and test micro-directives requiring citation (e.g., extending IDs 30-32 from `https://www.google.com/search?q=ROADMAP.md.txt`).
* **Search Engine Demo (Conceptual):** Develop a conceptual demonstration or whitepaper on how search engines could potentially filter or rank content based on CANDELA's on-chain hashes, promoting verified content.
* **Initial Academic Case Study / Workshop Paper:** Based on the MVP and early testing results, prepare and submit a paper to a relevant workshop or conference.

## Phase 0.5: Public Beta & Community Building (Target: Q4 2025 - Q1 2026)

* **Public Beta Release:** Offer a more polished version of the Guardian for public testing.
* **Browser Plug-in (Proof-of-Concept):** Develop a simple browser extension to query the CANDELA blockchain and visually indicate if web content is CANDELA-signed (as per `https://www.google.com/search?q=ROADMAP.md.txt`).
* **Community Engagement:** Actively build a community around CANDELA (e.g., Discord, regular updates).
* **Explore Creator Economy Integration:** Refine and prototype the "Creator Wallet" concept for tipping and revenue splits based on CANDELA-verified content.

## Phase 1.0 and Beyond: Production & Ecosystem Growth

* **Full Validator Suite:** Comprehensive validation for all applicable directives.
* **Mainnet Anchoring:** Transition from testnet to a mainnet blockchain for production use cases.
* **Integration with Existing Audit Platforms:** Explore partnerships or APIs to feed CANDELA's pre-execution proofs into post-execution audit systems (e.g., FICO, Prove AI).
* **DAO Governance:** Migrate project governance to a Decentralized Autonomous Organization as the community and adoption grow.
* **Standardization Efforts:** Work towards broader adoption and potential standardization of directive-driven AI governance.

This roadmap is a living document and will be updated as the project progresses and receives community feedback.

3. PROJECT_BRIEF.md (Concise Overview)

(Located in docs/ folder)
Markdown

# CANDELA – Project Brief (v0.1.1)

## Elevator Pitch

**CANDELA adds a blockchain-anchored Directive Guardian layer in front of any Large Language Model (LLM). It transforms fragile prompt rules into verifiable, auditable AI governance.**

---

## The Problem: Unreliable & Opaque AI

Current LLMs, while powerful, suffer from issues like hallucination, instructional drift, and lack of transparency. This makes them risky for critical applications and erodes trust. Existing solutions often focus on post-hoc logging, which doesn't guarantee the rules applied *before* the AI responded.

## CANDELA's Solution: Verifiable Pre-Execution Governance

CANDELA introduces the **Directive Guardian**, a middleware system that:

1.  **Loads a human-readable "directive scaffold"**: A set of clear rules for LLM behavior.
2.  **Verifies Rule Integrity via Blockchain**: Before use, the Guardian confirms the directive set's authenticity by checking its cryptographic hash against a record on a public blockchain.
3.  **Guides the LLM**: Strategically incorporates these verified directives into LLM prompts.
4.  **Validates LLM Output**: Automatically checks the LLM's response against the directives using programmed logic.
5.  **Ensures Accountability**: Enables an auditable trail from the enforced rules to the LLM's behavior.

---

## Key Innovations & Benefits

* **Pre-Execution Anchoring**: Ensures the rule-set is tamper-proof *before* the LLM generates a response.
* **Micro-Directives**: Breaks down complex concepts (e.g., "first-principles reasoning") into small, testable steps, making abstract rules operational and LLM-agnostic.
* **Transparency & Auditability**: Human-readable rules and blockchain records offer clear oversight.
* **Combating "AI Slop" & Supporting Creators**: By enabling verifiable content, CANDELA can help identify quality information and potentially facilitate direct rewards to original content creators, fostering a healthier digital ecosystem.

---

## Current Status (May 2025 - v0.1)

* **Proof-of-Concept (PoC) Complete**:
    * `directives_schema.json` (v3.2): 76 rules defined, including examples of micro-directives for "Associative Reasoning" and "First-Principles."
    * `guardian_prototype.py`: Python script demonstrates loading directives, SHA-256 hashing, and mock LLM/blockchain interaction. Successfully generates a verifiable hash of the directive bundle.
* **Initial Documentation Suite**: README, FAQ, Technical Specification, Directive Schema Guide, and this Project Brief are available in the [CANDELA GitHub Repository](https://github.com/jebus197/CANDELA). *(Link to be updated if it's not jebus197/CANDELA)*

---

## Core Components (Conceptual)

* **Directive Guardian**: Python-based middleware.
* **Directive Schema**: Machine-readable JSON format for directives.
* **Validation Tiers**: Directives categorized as "auto" (automated checks in PoC/MVP), "semi" (requiring heuristics), or "human" (requiring policy engine/manual review) for phased implementation.
* **Blockchain Anchoring**: Utilizing a public blockchain (e.g., Polygon testnet initially) for immutability.

---

## Roadmap Snapshot

| Phase                        | Key Milestone                                     | Target      |
| :--------------------------- | :------------------------------------------------ | :---------- |
| **v0.2 (Jun-Jul 2025)** | Implement Validation Tiers & Testnet Anchoring    | Planned     |
| **v0.3 (Jul-Aug 2025)** | Enhanced Validation, Semantic Linking (PoC)       | Planned     |
| **v0.4 (Aug-Q4 2025)** | Guardian flags low-confidence, "Must-Cite" rule   | Planned     |
| **v0.5 (Q4 2025 - Q1 2026)** | Public Beta, Creator Wallet/Tipping (PoC)       | Planned     |

*See the full [https://www.google.com/search?q=ROADMAP.md](https://www.google.com/search?q=ROADMAP.md) for more details.*

---

## Quick Start & Getting Involved

```bash
# Clone the repository
git clone [https://github.com/jebus197/CANDELA.git](https://github.com/jebus197/CANDELA.git) # Update URL if needed
cd CANDELA

# Install dependencies
pip install -r requirements.txt

# Run the minimal proof-of-concept
python src/guardian_prototype.py

We welcome contributions and feedback! Please check out the issues tab on GitHub. (Link to be updated)

CANDELA – Illuminating AI governance through verifiable directives.


### 4. FAQ.md (Key Questions Answered)

**(Located in `docs/` folder)**

```markdown
# CANDELA – Frequently Asked Questions

---

### 1. What problem does CANDELA solve?

LLMs can be unreliable, producing incorrect information or straying from instructions. It's also hard to know exactly what rules governed their responses. CANDELA provides a transparent and verifiable way to guide and audit LLM behavior using a predefined set of rules anchored on a blockchain.

---

### 2. Why "micro-directives"?

Abstract instructions like “be logical” are hard for LLMs to follow consistently and even harder to check automatically. CANDELA breaks these down into smaller, concrete "micro-directives" (e.g., for "First-Principles Reasoning": 1. Restate problem concisely. 2. List key facts. 3. Build answer from these facts.). This makes LLM behavior more predictable and easier for our "Guardian" system to validate.

---

### 3. How is CANDELA different from FICO Auditable AI or Prove AI?

Those are excellent systems for *post-hoc* auditing – they record what a model or its data lineage *was*. CANDELA focuses on *pre-execution* integrity – it anchors the *rules the LLM is supposed to follow* on the blockchain *before* it even generates a response. This provides an auditable record of intent and can complement post-hoc logging for end-to-end provenance.

---

### 4. Why use a blockchain?

The blockchain provides an immutable (unchangeable) and time-stamped public record of the exact directive set that was in force. Anyone can cryptographically verify that the rules haven't been tampered with, ensuring transparency and trust in the AI's governance.

---

### 5. Is CANDELA just "chain-of-thought" prompting?

While both involve breaking down tasks, CANDELA goes further. Standard chain-of-thought is embedded in the prompt and offers no lasting record or external validation. CANDELA stores the micro-directives in a verifiable, anchored schema and uses its Guardian system to actively validate the LLM's output against these rules. This provides a level of auditability and robust enforcement that simple prompting lacks.

---

### 6. Does the "Directive Guardian" need to be a super-smart AI?

No. The Guardian is a conventional software system. It uses programmed logic (like checking for keywords, specific formatting, or step-completion in micro-directives) to validate the LLM's output. It doesn't need to "understand" the concepts in a human way, only to execute its programmed checks. The LLM is still the "brains" for generation; the Guardian is the rule-enforcer.

---

### 7. How does CANDELA help combat "AI slop" or support content creators?

By providing a mechanism for verifiable content generation, CANDELA can help distinguish quality, rule-governed AI output from unverified "slop." Furthermore, because the directive set and output can be uniquely hashed and linked to a creator (e.g., via a wallet address in the metadata), it opens possibilities for:
* **Verifiable Attribution:** Clearly identifying the source and governing principles of AI-assisted content.
* **Quality Incentives:** Platforms could potentially prioritize or reward content that adheres to verifiable quality standards.
* **Creator Royalties/Tipping:** Enabling direct financial recognition for creators of high-quality original content that might be summarized or built upon by AIs, using the on-chain record to facilitate payments.

---

### 8. Is CANDELA open source?

Yes! All core components like the directive schema and prototype Guardian code are MIT-licensed. We encourage community contributions.

---

### 9. What's the current status and roadmap?

CANDELA is currently at the Proof-of-Concept stage (v0.1). We've demonstrated the core hashing mechanism. Key next steps include building out the Guardian's validation capabilities, integrating with live LLMs and testnet blockchains, and conducting empirical testing. See our [https://www.google.com/search?q=ROADMAP.md](https://www.google.com/search?q=ROADMAP.md) for details.

---

### 10. How can I get involved or learn more?

* **Star & Watch** our [GitHub Repository](https://github.com/jebus197/CANDELA) *(Update link if needed)*.
* Read our [Project Brief](docs/PROJECT_BRIEF.md) and [Technical Specification](TECH_SPEC.md).
* Check out the [issues tab](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/jebus197/CANDELA/issues) on GitHub for bugs, feature requests, or to contribute.
* *(A Discord or community forum link will be added here once established).*

---

*CANDELA – Illuminating AI governance through verifiable directives.*

5. directives_README.md (Guide to the Schema)

(Located in docs/ folder)
Markdown

# CANDELA Directive Schema – A Human Guide

This document explains the structure and intent behind `src/directives_schema.json`, the machine-readable heart of the CANDELA framework.

---

## Purpose of the Schema

The `directives_schema.json` file defines the complete set of rules, or "directives," that the CANDELA Guardian system uses to guide and validate the behavior of a Large Language Model (LLM). It's designed to be both human-readable (to understand the rules) and machine-parsable (for the Guardian to load and use).

---

## Key Fields in Each Directive Object

Each directive in the JSON array is an object with several key fields:

| Field                 | Meaning                                                                                                | Example Value                                     |
| :-------------------- | :----------------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| `id`                  | A unique numerical identifier for the directive.                                                       | `3`                                               |
| `sub` (optional)      | A sub-identifier (e.g., "a", "b", "c") used for micro-directives that break down a complex concept.      | `"a"` (for directive `6a`)                      |
| `text`                | The natural-language statement of the rule as it would be understood by a human or presented to an LLM. | `"Truthfulness & Non-Deception – no knowingly false information."` |
| `category`            | A broad functional grouping (e.g., "Ethical", "Reasoning", "Monitoring", "Communication", "Simplify"). | `"Ethical"`                                       |
| `notes` (optional)    | Brief explanatory notes for human reviewers.                                                           | `"No hallucination."`                             |
| `validation_tier`     | Indicates how compliance is checked: "auto", "semi", or "human".                                       | `"auto"`                                          |
| `validation_criteria` | Describes the logic for the Guardian to validate compliance (e.g., a regex, keyword, structural check). | `"Must include confidence tag."`                  |

---

## Understanding Micro-Directives

A core feature of CANDELA is the use of "micro-directives" to make complex or abstract behavioral goals operational and testable. Instead of a single vague directive like "Reason using first principles," we decompose it into a series of smaller, concrete, and verifiable steps.

**Example: First-Principles Reasoning (ID 24)**

The abstract goal is "Apply First-Principles Reasoning." This is broken down into:

* **24a:** "First-Principles – step 1: restate the problem in ≤15 words, no jargon." (Validation: check word count, potentially a jargon filter later).
* **24b:** "First-Principles – step 2: list the two most fundamental facts involved." (Validation: check for two distinct bullet points/facts).
* **24c:** "First-Principles – step 3: build the answer from those facts in clear language." (Validation: harder, might initially be `semi` or `human` tier, or check for presence of keywords from 24b in the answer).

This approach allows the Guardian validator to apply simpler, more reliable checks (like word counts or pattern matching) while collectively guiding the LLM toward the desired complex behavior.

---

## Worked Micro-Directive Examples (from v0.1 Schema)

The following tables illustrate how micro-directives are structured for automated validation in the current Proof-of-Concept.

### EX1 – Associative Reasoning (ID 14)

| Sub-ID | Step                                          | Micro-Directive (≤ words)                                            | Auto Check (v0.1)      |
| :----- | :-------------------------------------------- | :------------------------------------------------------------------- | :--------------------- |
| 14a    | Identify a tangential concept                 | "Associative Reasoning – step 1: list one tangential concept (≤5 words)." | Line starts with `Related:` |
| 14b    | Explain the link (≤ 25 words)                 | "Associative Reasoning – step 2: explain in ≤25 words how it connects back to the topic." | ≤ 25 words             |
| 14c    | State one practical implication (≤ 30 words)  | "Associative Reasoning – step 3: state one practical implication (≤30 words)."  | ≤ 30 words             |

### EX2 – First-Principles (ID 24)

| Sub-ID | Step                             | Micro-Directive                                                                 | Auto Check (v0.1)      |
| :----- | :------------------------------- | :------------------------------------------------------------------------------ | :--------------------- |
| 24a    | Restate the problem (≤ 15 words) | "First-Principles – step 1: restate the problem in ≤15 words, no jargon."       | ≤ 15 words             |
| 24b    | List two fundamental facts       | "First-Principles – step 2: list the two most fundamental facts involved."      | Exactly two bullet points |
| 24c    | Build answer from facts (≤ 100 words) | "First-Principles – step 3: build the answer from those facts in clear language." | ≤ 100 words            |

---

## Validation Tiers Explained

To manage the complexity of validating all directives, they are assigned a `validation_tier`:

* **`auto`**: Fully machine-checkable with current PoC capabilities (e.g., regex, word counts, simple structural checks).
* **`semi`**: Planned for future automated validation, likely requiring more advanced heuristics or lightweight NLP models (e.g., checking for sentiment that contradicts a "suppress emotional tone" directive).
* **`human`**: Inherently subjective or complex rules that will likely always require human oversight or a sophisticated policy engine to adjudicate (e.g., the full nuance of "Do no harm"). The Guardian would flag these for review.

In the v0.1 Proof-of-Concept, the Guardian primarily focuses on demonstrating checks for `auto` tier directives. The roadmap outlines the phased implementation of more complex validation.

---

## Versioning and Immutability

The `directives_schema.json` file is version-controlled within the GitHub repository. Critically, a cryptographic hash (SHA-256) of the *entire canonical directive bundle* is generated. This hash is then anchored on a public blockchain.

Any change to the text, ID, category, or validation criteria of any directive will result in a new, different hash.
* This ensures that the exact version of the rule-set in force at any given time is verifiable and tamper-proof.
* Updates to the directive set will be managed with semantic versioning (e.g., v0.1, v0.2, v1.0) as detailed in the `TECH_SPEC.md`.

---

This guide helps understand the structure and intent of the CANDELA directives. For precise technical details, please refer to `TECH_SPEC.md` and the `src/directives_schema.json` file itself.*

Last updated: 2025-05-15