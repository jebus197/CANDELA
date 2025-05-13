# Directive Schema – Human Guide

This document explains how to read and extend `src/directives_schema.json` and why **micro-directives** are used.

| Field | Meaning |
|-------|---------|
| `id` / `sub` | Unique identifier (letters mark micro-directives). |
| `text` | Natural-language rule given to the LLM. |
| `category` | Broad grouping (Ethical, Reasoning, Monitoring, etc.). |
| `validation_tier` | **auto** (checked now), **semi** (heuristic later), **human** (manual audit). |
| `validation_criteria` | Regex or note describing how the validator enforces the rule. |

---

## Micro-directive examples (present in v0.1 schema)

| ID | Purpose | Validation check |
|----|---------|------------------|
| **14a** | *Associative Reasoning 1* – list one tangential concept (≤ 5 words). | Line starts with `Related:` |
| **14b** | *Associative Reasoning 2* – explain the connection in ≤ 25 words. | ≤ 25 words |
| **14c** | *Associative Reasoning 3* – state one practical implication (≤ 30 words). | ≤ 30 words |
| **24a** | *First-Principles 1* – restate the problem in ≤ 15 words. | ≤ 15 words |
| **24b** | *First-Principles 2* – list two fundamental facts. | Exactly two bullet points |
| **24c** | *First-Principles 3* – build the answer from those facts (plain language, ≤ 100 words). | ≤ 100 words |

These small, testable steps let the Guardian validator enforce higher-level reasoning without deep semantic parsing.

---

## Validation tiers

* **auto**  – fully machine-checkable now (regex, word-count, simple heuristics).  
* **semi**  – slated for a future lightweight model or heuristic.  
* **human** – requires manual or policy-engine review.

Only the *auto* rules are enforced in version 0.1; *semi* and *human* rules trigger a flag or audit note.

---

## Roadmap

| Version | Milestone |
|---------|-----------|
| v 0.1 | Core-15 schema + anchoring Proof of Concept (this release). |
| v 0.2 | Expand micro-directives to additional `semi` rules; enhance validator. |
| v 0.3 | Deploy small heuristic model for uncertainty checks; integrate CI suite. |
| v 1.0 | Full directive coverage and on-chain anchoring in production. |

Only directives present in `directives_schema.json` are enforceable at runtime; additional micro-directives listed here appear in later versions.

---

*Last updated 2025-05-19*  
Repository: <https://github.com/jebus197/candela-llm-layer>
