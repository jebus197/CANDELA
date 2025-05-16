# CANDELA Directive Schema – Human Guide (v3.2)

This document explains how to read and extend the `src/directives_schema.json` file, which forms the machine-readable "Directive Scaffold" for the CANDELA project. It also clarifies why CANDELA utilizes "micro-directives" for complex concepts.

---

## Purpose of the Directive Schema

The `src/directives_schema.json` file defines the complete set of rules, or "directives," that the CANDELA "Directive Guardian" system uses to guide and validate the behavior of a Large Language Model (LLM). It's designed to be:

* **Human-Readable:** Allowing project maintainers, reviewers, and the community to understand the specific rules governing the AI.
* **Machine-Parsable:** Enabling the Guardian software to load, verify, and utilize these directives programmatically.
* **Version-Controlled & Verifiable:** The entire schema file is cryptographically hashed (SHA-256), and this hash is anchored on a public blockchain (testnet for PoC). This allows anyone to verify the integrity and authenticity of the directive set being used at any given time.

---

## Key Fields in Each Directive Object (within `directives_schema.json`)

Each directive in the JSON array is an object with several key fields:

| Field                 | Meaning                                                                                                 | Example Value (from schema)                     |
| :-------------------- | :------------------------------------------------------------------------------------------------------ | :---------------------------------------------- |
| `id`                  | A unique numerical identifier for the main directive.                                                 | `3`                                             |
| `sub` (optional)      | A sub-identifier (e.g., "a", "b", "c") used for micro-directives that break down a complex parent `id`. | `"a"` (for micro-directive `6a`)                |
| `text`                | The natural-language statement of the rule as it would be understood by a human or presented to an LLM. | `"Truthfulness & Non-Deception – no knowingly false information."` |
| `category`            | A broad functional grouping (e.g., "Core", "Ethical", "Reasoning", "Monitoring", "Communication", "Simplify", "Meta", "Policy", "Content", "Interaction", "Uncertainty", "Transparency", "Admin"). | `"Ethical"`                                     |
| `notes` (optional)    | Brief explanatory notes for human reviewers regarding the directive's intent or application.            | `"No hallucination."`                           |
| `validation_tier`     | (Currently conceptual for many, implemented for some "auto") Indicates how compliance is planned to be checked: "auto" (automated), "semi" (heuristic/NLP-assisted), or "human" (manual/policy engine). | `"auto"`                                        |
| `validation_criteria` | Describes the logic or pattern for the Guardian to validate compliance (e.g., a regex, keyword, structural check, word count). For many directives, this is "N/A" in v0.1 PoC, indicating future development. | `"Must include confidence tag."`                |

---

## The CANDELA "Micro-Directive" Strategy

A core feature of CANDELA is the use of **"micro-directives"** to make complex or abstract behavioral goals (often referred to as "meta-directives" in our discussions) operational and more readily testable. Instead of a single, potentially ambiguous directive like "Reason using first principles," CANDELA aims to decompose such concepts into a series of smaller, concrete, and verifiable steps.

**Why Micro-Directives?**

* **Clarity for LLMs:** Smaller, explicit steps are generally easier for LLMs to "follow" (i.e., generate statistically compliant output) than broad, abstract commands.
* **Testability for the Guardian:** It's more feasible for the Guardian software to perform automated checks against well-defined, granular steps (e.g., "Does the output contain exactly two bullet points labeled 'Fact 1' and 'Fact 2'?") than to validate "Did the LLM use first principles?" holistically.
* **Modularity & Extensibility:** Micro-directives can be combined or refined more easily as the system evolves.
* **Transparency:** The decomposition makes the intended reasoning process more explicit for human reviewers.

### Worked Micro-Directive Examples (from `directives_schema.json` v3.2)

The following tables illustrate how micro-directives are structured. The "Validation check (v0.1 PoC)" column indicates how these might be simply checked in the current PoC, with more sophisticated validation planned for future versions.

**Example 1: Associative Reasoning (Decomposition of a complex cognitive task - ID 14)**

| Sub-ID | Step                                         | Micro-Directive (from schema)                                                                 | Validation check (v0.1 PoC Example) |
| :----- | :------------------------------------------- | :-------------------------------------------------------------------------------------------- | :---------------------------------- |
| 14a    | Identify a tangential concept                | "Associative Reasoning – step 1: list one tangential concept (≤5 words)."                     | Response contains "Related:" & word count |
| 14b    | Explain the connection (≤ 25 words)          | "Associative Reasoning – step 2: explain in ≤25 words how it connects back to the topic."     | Word count of relevant section      |
| 14c    | State one practical implication (≤ 30 words) | "Associative Reasoning – step 3: state one practical implication (≤30 words)."                | Word count of relevant section      |

**Example 2: First-Principles Reasoning (Decomposition of a problem-solving heuristic - ID 24)**

| Sub-ID | Step                            | Micro-Directive (from schema)                                                                 | Validation check (v0.1 PoC Example) |
| :----- | :------------------------------ | :-------------------------------------------------------------------------------------------- | :---------------------------------- |
| 24a    | Restate the problem (≤ 15 words)  | "First-Principles – step 1: restate the problem in ≤15 words, no jargon."                   | Word count of restatement           |
| 24b    | List two fundamental facts      | "First-Principles – step 2: list the two most fundamental facts involved."                  | Checks for two distinct facts/bullets |
| 24c    | Build answer from facts         | "First-Principles – step 3: build the answer from those facts in clear language."             | Checks for presence of fact keywords in answer |

*Note: The `validation_criteria` field in `directives_schema.json` provides more specific intended checks for developers.*

---

## Validation Tiers Explained

To manage the development complexity of validating all 76 directives, they are conceptually assigned a `validation_tier` in the schema (though this field is primarily for planning in v0.1 and not yet fully utilized by `guardian_poc_v0.1.py` for all directives):

* **`auto`**: Directives intended to be fully machine-checkable with current or near-future Guardian capabilities (e.g., using regular expressions, word counts, simple structural checks, keyword spotting). The micro-directive examples above are targeted for "auto" validation. Directives 71-74 (Confidence, Narrative Confidence, Critical Review, Concise Response) also have "auto" potential.
* **`semi`**: Directives that may require more advanced heuristics, lightweight Natural Language Processing (NLP) models, or more complex programmed logic for automated validation. These are targets for later MVP stages and beyond. (e.g., Directive 8 "Reject hallucinated confidence," Directive 10 "Disclose uncertainty explicitly").
* **`human`**: Inherently subjective or highly complex ethical rules that will likely always require some level of human oversight or a sophisticated external policy engine to adjudicate fully (e.g., Directive 2 "Do no harm," Directive 35 "Only redact or suppress output when structurally necessary for coherence or safety"). The Guardian might flag outputs related to these for human review.

In the current v0.1 Proof-of-Concept, the `guardian_poc_v0.1.py` script demonstrates only very basic validation for a couple of illustrative directives. Full implementation of "auto" tier checks is a primary goal for the MVP (v0.2/v0.3) as per the [ROADMAP.md](ROADMAP.md).

---

## Versioning and Immutability

The `src/directives_schema.json` file is version-controlled (currently v3.2). A cryptographic hash (SHA-256) of this canonical directive bundle is generated (see `README.md` for the current hash). This hash is the item anchored on the blockchain.

* Any change to the directive set (text, ID, category, validation criteria, etc.) will result in a new, different hash.
* This ensures that the exact version of the rule-set intended to be in force is verifiable and tamper-proof.
* Updates to the directive set will be managed with semantic versioning and new blockchain anchors, as detailed in `TECH_SPEC.md`.

---

*This guide helps understand the structure and intent of the CANDELA directives. For precise technical details, please refer to `TECH_SPEC.md` and the `src/directives_schema.json` file itself.*

*Last Updated: May 16, 2025*
*Repository: [https://github.com/jebus197/CANDELA](https://github.com/jebus197/CANDELA)* *Copyright (c) 2024-2025 George Jackson (CANDELA Project Lead). MIT Licensed.*