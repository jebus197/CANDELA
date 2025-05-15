# CANDELA

**Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

*Illuminate AI behaviour through verifiable, pre-execution rule anchoring.*

---

## The Challenge: Making AI Reliable and Transparent

Large Language Models (LLMs) are powerful tools, but they can be unpredictable. They might provide incorrect information ("hallucinate"), stray from initial instructions, or offer inconsistent answers. Because their internal reasoning is often a "black box," it's hard to trust them for critical tasks or understand *why* they produce a specific output. This lack of reliability and transparency is a major hurdle for the safe and widespread use of AI.

**CANDELA addresses this by introducing the Directive Guardian: an external, verifiable system that guides and constrains LLM behaviour.**

➡ **For a two-minute overview, see our [Project Brief](docs/PROJECT_BRIEF.md).**

---

## How CANDELA Works: A Solution Overview

CANDELA uses a "Directive Guardian" – a smart software layer that sits between the user (or an application) and the LLM. Here’s the basic idea:

1.  **Define the Rules (Directives):** We start with a clear, human-readable set of rules called "directives." These tell the LLM how it should behave (e.g., be truthful, disclose uncertainty, follow specific reasoning steps). For complex ideas, we break them down into smaller, testable "micro-directives." (Learn more in our [Directive Schema Guide](docs/directives_README.md)).
2.  **Secure the Rules (Blockchain Anchoring):** Before the LLM even starts, the Guardian takes a digital fingerprint (a SHA-256 hash) of these directives and records it on a public blockchain. This ensures the rules are tamper-proof and auditable – everyone can see what rules were supposed to be in effect.
3.  **Guide the LLM (Strategic Prompting):** The Guardian intelligently incorporates these verified directives into the instructions (prompts) given to the LLM. This "nudges" the LLM to produce responses that align with the rules.
4.  **Check the Work (Output Validation):** After the LLM responds, the Guardian automatically checks the output against the specific micro-directives. This isn't about understanding like a human, but about programmed checks for compliance (e.g., did it include a confidence score? Did it follow the reasoning steps?).
5.  **Enforce and Log (Action Handling):**
    * If the output complies: It's passed to the user.
    * If it violates a rule: The Guardian can flag the issue, ask the LLM to try again, or prevent the non-compliant output from being shown.
    * (Optional) For a complete audit trail, a fingerprint of the entire interaction (input, directives, and output) can also be anchored on the blockchain.

This system transforms a potentially unreliable LLM into a more predictable and accountable tool by wrapping it in a verifiable governance framework.

---
## Key Features

* **Pre-Execution Rule Anchoring:** Ensures the integrity of behavioural rules *before* the LLM acts.
* **Micro-Directives:** Makes complex reasoning concepts operational and testable. (See examples in [Extended Micro-Directive Templates](README.md#extended-micro-directive-templates-doc-only) below).
* **Transparent & Auditable:** Human-readable rules and blockchain verification provide clear oversight.
* **Modular & Model-Agnostic:** Designed to work as a layer on top of various LLMs.
* **Creator-First Potential:** By anchoring content with its rule-set and potentially a creator's wallet, CANDELA could help ensure quality and enable fairer revenue models in the digital content ecosystem, combating "AI slop."

---
## Extended Micro-Directive Templates (Illustrative for Future Versions)

To show how CANDELA can handle more complex reasoning, here are examples of how abstract directives can be broken down into verifiable steps. *(These richer versions are planned for future releases; the current prototype uses simplified versions for initial demonstration.)*

**Granular Associative-Reasoning (Example ID 14a-f)**

| Sub-ID | Step                                          | Micro-Directive                                            | Auto-check             |
| :----- | :-------------------------------------------- | :--------------------------------------------------------- | :--------------------- |
| 14a    | Surface concept                               | "**Related:** *<≤3 words>*"                                | line starts `Related:` |
| 14b    | Type of link                                  | "**LinkType:** analogy / contrast / cause-effect / subset" | regex                  |
| 14c    | 1-sentence bridge (≤ 20 words)                | —                                                          | word-count             |
| 14d    | Domain relevance tag (e.g., physics / ethics) | "**Domain:** …"                                            | whitelist              |
| 14e    | Practical implication (≤ 30 words)            | —                                                          | word-count             |
| 14f    | Confidence 0-1                                | "**Conf:** 0.00-1.00"                                      | float range            |

**Granular First-Principles (Example ID 24a-f)**

| Sub-ID | Step                             | Micro-Directive           | Auto-check     |
| :----- | :------------------------------- | :------------------------ | :------------- |
| 24a    | Problem restatement (≤ 12 words) | —                         | word-count     |
| 24b    | Fact 1                           | "• F1 … (≤ 10 words)"     | bullet + count |
| 24c    | Fact 2                           | "• F2 … (≤ 10 words)"     | bullet + count |
| 24d    | Hidden assumption? yes/no        | "**Assumption?:** yes/no" | yes/no         |
| 24e    | Derived principle (≤ 25 words)   | —                         | word-count     |
| 24f    | Final answer (≤ 80 words)        | —                         | word-count     |

---
## Current Directive + I/O Fingerprints (Proof-of-Concept v0.1)

| Item                   | SHA-256 Hash                                                     |
| :------------------------- | :--------------------------------------------------------------- |
| **Directive bundle** | `3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa` |
| **Session I/O** (example)| `e637b47f826fca642f8e7de6461a671f7ae70e64595af447d7b43f85f8fda086` |

*Generated by `src/guardian_prototype.py` on 2025-05-12.*
*Any change to `src/directives_schema.json` (or the LLM's response to a given prompt) will produce a different hash, ensuring full traceability.*

**Note:** For a commented, human-friendly version of the directive structure and micro-directive examples, see [`docs/example_directives_schema_annotated.jsonc`](docs/example_directives_schema_annotated.jsonc). The actual runtime schema (`src/directives_schema.json`) must remain strict, comment-free JSON for reliable parsing.

---
## Repository Structure

| Path                         | Purpose                                                 |
| :--------------------------- | :------------------------------------------------------ |
| `docs/`                      | Human-readable documents (Project Brief, FAQ, Diagrams) |
| `src/guardian_prototype.py`  | Minimal runnable Proof-of-Concept (PoC)                 |
| `src/guardian_extended.py`   | Richly commented workflow with anchoring template       |
| `src/directives_schema.json` | Machine-readable directive list (v3.2, 76 items)        |
| `requirements.txt`           | Python dependencies                                     |
| `TECH_SPEC.md`               | Architecture overview & developer to-dos                |
| `tests/`                     | (Placeholder for unit tests)                            |

---
## Quick Start

```bash
# 1. Clone the repository
git clone [https://github.com/jebus197/CANDELA.git](https://github.com/jebus197/CANDELA.git)
cd CANDELA

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the minimal demo
python src/guardian_prototype.py

# Or run the extended flow (future blockchain anchoring)
# python src/guardian_extended.py