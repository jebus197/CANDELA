# Directive Schema – Human Guide

This document explains how to read and extend `src/directives_schema.json`.

| Field | Meaning |
|-------|---------|
| `id` / `sub` | Unique identifier (letters mark micro-directives). |
| `text` | Natural-language rule given to the LLM. |
| `category` | Broad grouping (Ethical, Reasoning, Monitoring…). |
| `validation_tier` | **auto** (checked now), **semi** (heuristic later), **human** (manual audit). |
| `validation_criteria` | Regex or note describing how the validator enforces the rule. |

## Why micro-directives?
Complex concepts (e.g., *“first-principle reasoning”, from engineering, otherwise known as the KISS principle*) are decomposed into small, testable steps:
24a. Restate the problem in ≤15 words
24b. List two fundamental facts
24c. Build the answer from those facts in plain language

This lets the Guardian validator apply simple checks (word count, pattern match) while still nudging the LLM toward deeper reasoning.

## Versioning
Any change to directive text or IDs requires:
1. Bumping the schema version (see TECH_SPEC).  
2. Re-anchoring the new SHA-256 hash on the blockchain.  
3. Updating this README if fields change.
