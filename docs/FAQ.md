# CANDELA – Frequently Asked Questions (FAQ)

This FAQ addresses common questions about the CANDELA project's methodology, goals, and technical implementation. For a quick overview, please see our [Project Brief](PROJECT_BRIEF.md).

---

### 1. What problem does CANDELA solve?

AI models (including Large Language Models (LLMs) like GPT) can be powerful, but they sometimes produce incorrect information ("hallucinate"), drift from their original instructions, or give inconsistent answers. It's also often unclear *why* they respond a certain way, as their internal workings can be like a "black box." This lack of reliability and transparency makes it risky to use them for important tasks.

CANDELA aims to solve this by creating a verifiable governance layer. It uses a "Directive Guardian" (a software intermediary) to ensure an LLM follows a clear, human-readable set of rules (the "Directive Scaffold"). The integrity of this rule-set is secured by anchoring its cryptographic hash (a unique digital fingerprint) on a public blockchain *before* the LLM generates any output.

---

### 2. Why does CANDELA use "micro-directives"?

Broad, abstract instructions like “apply first-principles reasoning” can be interpreted inconsistently by different LLMs and are hard to check automatically. CANDELA breaks down such complex concepts into smaller, concrete, and testable steps called **"micro-directives"** (e.g., for "First-Principles Reasoning": 1. Restate problem concisely. 2. List key facts. 3. Build answer from these facts).

This approach has several benefits:
* **Clarity:** Makes it easier for the LLM to "understand" (in a processing sense) what's expected.
* **Testability:** Allows the Guardian software to perform more precise, automated checks for compliance against these smaller steps.
* **Reproducibility:** Helps ensure more consistent behavior from the LLM.
* **Model-Agnosticism (Goal):** Well-defined micro-directives are less dependent on the internal quirks of a specific LLM.

(See our [Guide to the Directive Schema](directives_README.md) for more examples.)

---

### 3. How does CANDELA differ from systems like FICO Auditable AI or Prove AI?

Systems like FICO's Auditable AI and Prove AI are valuable for creating audit trails of AI models and their outputs *after* they have been generated (post-hoc logging). They often focus on model versioning, data lineage, and recording runtime logs.

CANDELA is complementary but distinct: its primary focus is on **pre-execution rule-set integrity and runtime guidance.** CANDELA anchors the *behavioral rule-set (the directives)* on the blockchain *before* the LLM generates a response. This ensures that the rules themselves are transparent and haven't been tampered with. The Guardian then uses these verified rules to guide and validate the LLM's behavior in real-time.

Combining CANDELA's pre-execution rule verification with post-execution logging from other systems could provide a very comprehensive, end-to-end provenance and accountability solution.

---

### 4. Why use a blockchain for the directives?

The blockchain is used for its core properties of **immutability and transparency,** not for cryptocurrency purposes.

1.  **Immutability:** Once the hash (unique fingerprint) of the `directives_schema.json` file is recorded on a public blockchain (like the Polygon Mumbai or Ethereum Sepolia testnets for our PoC), it cannot be secretly altered or deleted.
2.  **Transparency & Verifiability:** Anyone can independently take the official `directives_schema.json` from the CANDELA repository, calculate its SHA-256 hash, and compare it to the hash anchored on the blockchain. This proves that the rule-set being used by the Guardian (which performs this check at runtime) is the authentic, agreed-upon version.

This prevents "prompt drift" or unauthorized changes to the AI's governing rules from going undetected.

---

### 5. Is CANDELA just "chain-of-thought" prompting with a new name?

While both CANDELA's micro-directives and "chain-of-thought" (CoT) prompting involve breaking down complex tasks into smaller steps to guide LLM reasoning, CANDELA adds crucial layers:

* **Verifiable Rule-Set:** CoT steps are typically just part of the prompt. CANDELA's directives are defined in a structured schema, their integrity is anchored on-chain, and they are version-controlled.
* **External Validation:** CoT relies on the LLM correctly following the prompted steps. CANDELA's Guardian *externally validates* the LLM's output against the (micro-)directives.
* **Auditability:** CANDELA aims to create an auditable link between the specific, anchored directive set used and the LLM's behavior. Standard CoT does not offer this formal audit trail.

So, while CANDELA leverages the *principle* of guided, step-by-step reasoning, it embeds this within a framework of verifiable governance and explicit validation.

---

### 6. Does the "Directive Guardian" need to be a super-smart AI itself?

No. The Directive Guardian is conceived as **conventional software (middleware), not another general-purpose AI.** Its "intelligence" lies in its programmed logic to:
* Load and verify the directive set against the blockchain anchor.
* Construct prompts incorporating these directives.
* Execute specific, predefined validation checks (e.g., regex, keyword matches, structural checks for micro-directive steps, word counts) on the LLM's output.
* Handle compliance or non-compliance according to its programming.

It doesn't need to "understand" the directives in a human sense but rather to process them and the LLM's output according to its coded instructions.

---

### 7. How can CANDELA help address "AI Slop" or support content creators?

This is a longer-term vision for the CANDELA framework:

* **Verifiable Quality Signal:** By extending the system, standards for human-generated content (e.g., for originality, factual accuracy in journalism, citation in research) could also be defined and anchored. Content meeting these standards could receive a "Candela-Verified" stamp.
* **Filtering Content:** Search engines and platforms could potentially use this verification as a signal to prioritize high-quality, trustworthy content and filter out unverified "AI slop."
* **Creator Attribution & Monetization:** Linking verified content to a creator's digital wallet (via the on-chain record) could enable direct tipping, automated revenue sharing from platforms, or even the creation of "content tokens" representing ownership of verifiably high-quality original work.

This aims to create a healthier digital ecosystem where quality is more easily identifiable and creators are more equitably rewarded. (See `PROJECT_BRIEF.md` for more on this.)

---

### 8. Is CANDELA open source?

Yes, CANDELA is an open-source project licensed under the MIT License. We encourage community review, feedback, and contributions. All core documents and PoC code are available in our [GitHub repository](https://github.com/jebus197/CANDELA). ---

### 9. What does CANDELA actually enforce today?

This is a key reviewer question, and the answer is deliberately explicit.

In v0.3 (Research Beta), CANDELA enforces:
* A fast regex screen and a semantic screen (Mini-BERT), with strict mode as the default.
* A subset of directives with objective, machine-checkable `validation_criteria` (implemented without changing the anchored rule-set).

For the exact coverage list (what is enforced vs. documented intent), see:
* `VALIDATION_COVERAGE.md`

---

### 10. What is the current status and roadmap for CANDELA?

As of Feb 2026, CANDELA is at **v0.3 (Research Beta)**.
* The directive set (v3.2) is defined in `src/directives_schema.json` and its canonical SHA-256 is anchored on Sepolia (see `ANCHORS.md`).
* The runtime Guardian supports regex + semantic checks with strict mode as the default (`guardian_runtime.py`).
* Outputs are logged off-chain and batched into Merkle roots that can be anchored on-chain for auditability (`anchor_outputs.py`).

Key next steps, as outlined in our [ROADMAP.md](ROADMAP.md), include:
* Expanding directive enforcement coverage (more objective rules, fewer "N/A").
* Publishing benchmark evidence (p50/p95 latency, strict vs sync_light) and hardening the service layer.
* Building a reviewer-friendly proof UX for output verification (Merkle proofs against anchored roots).

---

### 11. How can I get involved or learn more?

* **Explore our GitHub Repository:** [https://github.com/jebus197/CANDELA](https://github.com/jebus197/CANDELA) * Read the [Project Brief](docs/PROJECT_BRIEF.md) and [Technical Specification](TECH_SPEC.md).
* Read the [Project Brief](PROJECT_BRIEF.md) and [Technical Specification](Tech_Spec.md).
* Review the [Directive Schema Guide](directives_README.md).
* Check the [Issues Tab](https://github.com/jebus197/CANDELA/issues) on GitHub for current tasks, to report bugs, or to suggest features. * *(A Discord or community forum link will be added here once established).*

We welcome feedback and collaboration as we develop CANDELA further!

---

*CANDELA – Illuminating AI governance through verifiable directives.*
*Copyright (c) 2024-2025 George Jackson (CANDELA Project Lead). MIT Licensed.*
