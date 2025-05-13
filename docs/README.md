# CANDELA

**Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**


Addressing the LLM "Black Box" & Reliability Challenge

A fundamental challenge in working with frontier Large Language Models (LLMs) is their inherent nature as probabilistic prediction engines. Unlike traditional software, LLMs do not execute explicit rules or logic programmatically. Their output is based on statistical patterns learned from vast training data, leading to well-documented issues such as hallucination, unpredictable drift from instructions, inconsistency, and a general lack of transparency in their reasoning process. This poses a significant hurdle for deploying LLMs in applications requiring high reliability, safety, and auditability.

Note:

➡ For a two-minute overview, see [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md)


This project tackles this challenge by introducing an external, verifiable system designed to guide and constrain LLM behaviour: the Directive Guardian. This architecture operates as middleware situated between the user/application layer and the core LLM API.

The Guardian system implements the following workflow:

    Directive Management & Verification: A core component loads a structured, human-readable directive set (defined in a schema, e.g., directives_schema.json ). This component performs cryptographic hashing (e.g., SHA-256) of the directives and verifies this hash against an immutable record anchored on a public blockchain. This ensures the integrity of the rule-set, confirming it has not been altered.   

Strategic Prompt Construction: User input is processed by the Guardian, which dynamically constructs the prompt sent to the LLM API. This involves incorporating the verified directives into the prompt context (e.g., via system messages or explicit in-line instructions) using advanced prompting techniques. This step aims to statistically bias the LLM's probabilistic output towards adherence to the directives.  
Output Validation & Enforcement: Upon receiving the raw, probabilistically generated output from the LLM, the Guardian's crucial validation component analyses it against the loaded directive set. This involves programmed logic to check for contradictions, hallucinated confidence, non-adherence to behavioural rules (e.g., disclosure of uncertainty, avoiding flattery), and structural requirements. This logic is external to the LLM itself.  
Action Handling: Based on the validation results, the Guardian determines the next step:

    If compliant: The output is passed to the user.
    If non-compliant: The Guardian can intercept the output, flag the specific directive violation, log the event, and potentially instruct the LLM to regenerate a corrected response based on the identified rule breach.   

Auditable Logging (Optional): The system can log interaction details (input, directives used, validation results, final output), potentially hashing these logs and anchoring them on the blockchain to create a transparent and auditable record of the AI system's behaviour and rule adherence attempts.  

This architecture addresses the LLM's inherent probabilistic nature by engineering an external framework that provides verifiable rule enforcement, transparency, and accountability. It transforms a potentially unreliable AI component into a more predictable and auditable system, without requiring fundamental changes to the LLM's core predictive mechanism. This approach, particularly the pre-execution anchoring of the behavioural rule-set, offers a novel angle  compared to systems that only anchor post-execution logs.


## Extended Micro-Directive Templates (doc-only)

The runtime schema uses 3-step versions for compact demos.  
Below are richer 6-step templates we will adopt in v0.2+ for deeper traceability…

Granular Associative-Reasoning (ID 14a-f) – doc-only example


| Sub-ID | Step                                          | Micro-Directive                                            | Auto-check             |
| ------ | --------------------------------------------- | ---------------------------------------------------------- | ---------------------- |
| 14a    | Surface concept                               | “**Related:** *<≤3 words>*”                                | line starts `Related:` |
| 14b    | Type of link                                  | “**LinkType:** analogy / contrast / cause-effect / subset” | regex                  |
| 14c    | 1-sentence bridge (≤ 20 words)                | —                                                          | word-count             |
| 14d    | Domain relevance tag (e.g., physics / ethics) | “**Domain:** …”                                            | whitelist              |
| 14e    | Practical implication (≤ 30 words)            | —                                                          | word-count             |
| 14f    | Confidence 0-1                                | “**Conf:** 0.00-1.00”                                      | float range            |


Granular First-Principles (ID 24a-f) – doc-only example

| Sub-ID | Step                             | Micro-Directive           | Auto-check     |
| ------ | -------------------------------- | ------------------------- | -------------- |
| 24a    | Problem restatement (≤ 12 words) | —                         | word-count     |
| 24b    | Fact 1                           | “• F1 … (≤ 10 words)”     | bullet + count |
| 24c    | Fact 2                           | “• F2 … (≤ 10 words)”     | bullet + count |
| 24d    | Hidden assumption? yes/no        | “**Assumption?:** yes/no” | yes/no         |
| 24e    | Derived principle (≤ 25 words)   | —                         | word-count     |
| 24f    | Final answer (≤ 80 words)        | —                         | word-count     |


## Current Directive + I/O Fingerprints

| Item                       | SHA-256 Hash |
|----------------------------|------------------------------------------------------------------|
| **Directive bundle**       | `3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa` |
| **Session I/O** (example)  | `e637b47f826fca642f8e7de6461a671f7ae70e64595af447d7b43f85f8fda086` |

Generated by `src/guardian_prototype.py` on **2025-05-12**.  
Any change to `src/directives_schema.json` (or the response payload) will produce a different hash, ensuring full traceability.


Note:

See examples/directives_schema_annotated.jsonc for a commented, reader-friendly version that demonstrates both the standard directive structure and the micro-directive structure of more complex prompts.; the runtime schema must remain comment-free for strict JSON execution.
