# Validation Coverage (v0.3 Research Beta)

This document makes enforcement coverage explicit so technical reviewers can see:
- what is currently enforced by code
- what is documented intent (not yet machine-checkable)
- what is conditionally enforced (only when an output opts into a specific format)

## Canonical directive bundle
- File: `src/directives_schema.json`
- Canonical SHA-256 (sorted keys, Unicode preserved): `7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d`
- Shape: list of directive objects
- Uniqueness: some directives are micro-steps and share the same numeric `id` with a `sub` key.
  - Unique key is `(id, sub)` where `sub` is optional.

## Counts (exact)
- Directive objects in JSON: 82
- Unique numeric IDs: 76
- Objects with explicit (non-N/A) `validation_criteria`: 18
- Objects with `validation_criteria: N/A`: 64

Micro-directive groups (same `id`, different `sub`):
- ID 6: 6a, 6b, 6c
- ID 14: 14a, 14b, 14c
- ID 24: 24a, 24b, 24c

## Enforcement layers
Always-on enforcement (independent of `validation_criteria`):
- Regex screen: `src/guardian_extended.py` (`hex_key`, `dob`, profanity)
- Semantic screen: `src/detectors/mini_semantic.py` (MiniLM / `all-MiniLM-L6-v2` via sentence-transformers), controlled by `config/guardian_scoring.yaml`

Directive-criteria enforcement (implemented in v0.3):
- Implemented in: `src/directive_validation.py`
- Integrated in: `src/guardian_runtime.py` (strict-by-default)
- Configuration: `config/guardian_scoring.yaml` under `validation:`

## Directive criteria coverage (explicit criteria only)

Legend:
- ENFORCED: machine-checked and can block (violation)
- ADVISORY: machine-detected but does not block by default
- CONDITIONAL: enforced only when output opts into that format (marker-based trigger)
- NOT IMPLEMENTED: criteria exists but is not yet machine-checkable in v0.3

### Confidence / uncertainty tags
- 3 / 71: Confidence tag
  - ADVISORY by default (missing confidence is noted)
  - ENFORCED if `validation.enforce_confidence_tag: true`
  - Format check ENFORCED when tag is present: `Confidence: High|Medium|Low`
- 10: `[uncertain]` tag
  - ENFORCED if `validation.enforce_uncertain_tag: true`

### Logical-Extension (ID 6, CONDITIONAL)
Triggered only if output contains a line starting with `Premise:` or `Inference:` (case-insensitive).
- 6a ENFORCED: must include `Premise:` line
- 6b ENFORCED: must include `Inference:` line
- 6c ENFORCED: `Inference:` content must be <= 20 words and end with a period

### Associative Reasoning (ID 14, CONDITIONAL)
Triggered only if output contains a line starting with `Related:` (case-insensitive).
- 14a ENFORCED: `Related:` line must exist
- 14b ENFORCED: next non-empty line after `Related:` must be <= 25 words
- 14c ENFORCED: next non-empty line after that must be <= 30 words

### First-Principles (ID 24, CONDITIONAL)
Triggered only if output contains a line starting with `First-Principles` (case-insensitive).
- 24a ENFORCED: restatement line must be <= 15 words
- 24b ENFORCED: exactly two bullet points (lines starting with `-` or `*`) in the First-Principles section
- 24c ENFORCED: First-Principles section must be <= 100 words (plain-language heuristics are not applied in v0.3)

### Explicit criteria present but not fully machine-checkable (v0.3)
These are intentionally NOT enforced yet because they require additional runtime signals (confidence scores, trigger conditions) or subjective judgment:
- 2: "No prohibited content." (covered by regex + semantic screens, but not a complete semantic policy engine)
- 8: "Must disclose uncertainty." (requires semantic assessment of uncertainty presence)
- 13: "When lapse detected, include explanation." (requires lapse detection signal)
- 72: "If confidence <0.85 include tag." (requires a numeric confidence signal)
- 73: "Shows header when triggered." (requires trigger logic and confidence signal)
- 74: "Response length check." (requires request context and a target length policy)

## Reviewer-facing takeaway
- v0.3 is explicit about what is enforced today vs. what is roadmap intent.
- The canonical directive bundle is anchored and verified; enforcement coverage is implemented for the objective criteria subset without changing the anchored rule-set.
