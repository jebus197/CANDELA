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
Complex concepts (e.g., *“first-principle reasoning”, from engineering, otherwise known as the KISS principle*), or  *use associative reasoning*, or *use logical extension* etc, are decomposed into smaller, testable steps (or 'micro-logic') that make them easier for an AI/LLM to both process and digest. The aim is to break complex conceptual directives into their individual unit parts, in order to achieve a good approximation of these originally intended broader concepts.

For Example:

24a. Restate the problem in ≤15 words

24b. List two fundamental facts

24c. Build the answer from those facts in plain language

24d Consider how well your response corresponds to what is known about a first principle approach to problem solving in enginnering

24e This is often referered to as the KISS approach to problem solving. (Keep It Simple Stupid.)

24f Consider this your benchmark for complex problems in questions addressing scioence, engineering, mathematics.

24g Link this to other relevant directives such as those addressing logical extension, associative reasoning etc.

24f Use this approach to arrive at the most accurate and novel solutions for problems of this nature you are presented with.

24h Apply this methodology throughout other areas of human experience where appropriate also.

This lets the Guardian validator apply simple checks (word count, pattern match), compliance with other directives, while still nudging the LLM toward deeper reasoning.

## Versioning
Any change to directive text or IDs requires:
1. Bumping the schema version (see TECH_SPEC).  
2. Re-anchoring the new SHA-256 hash on the blockchain.  
3. Updating this README if fields change.
