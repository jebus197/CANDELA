# CANDELA Ruleset Schema (Enterprise E1.0)

This file explains `src/directives_schema.json` for both technical and non-technical readers.

## What the ruleset is
The ruleset is a machine-readable list of checks the Guardian applies to text output.

The ruleset is anchored on-chain (via a SHA-256 of the canonical JSON) so a third party can verify:
- exactly which rules were in force
- that the rules were not silently changed after-the-fact

The on-chain anchor records live in `docs/ANCHORS.md`.

## File shape
`src/directives_schema.json` is JSON with:
- `meta`: human context (name, version, anchoring notes)
- `directives`: a list of directive objects

## Directive fields (what they mean)
Each directive has:
- `id`: integer identifier (stable reference)
- `title`: short name
- `category`: broad grouping (Security, Privacy, Safety, Transparency)
- `validation_tier`:
  - `BLOCK`: the Guardian blocks output when the rule triggers
  - `WARN`: the Guardian records a warning, but does not block by default
- `validation_criteria.checks`: a list of machine-checkable checks

## Check kinds (current)
The current ruleset uses these `kind` values:
- `regex_forbid`: flags when any pattern matches
- `regex_require`: flags when a required pattern is missing
- `luhn_card_forbid`: flags likely payment card numbers (Luhn-positive digit sequences)
- `semantic_forbid`: flags text that is semantically similar to prohibited intent phrases

## Where checks are enforced
- Deterministic checks: `src/directive_validation.py`
- Semantic similarity: `src/detectors/mini_semantic.py`
- Runtime integration and modes: `src/guardian_runtime.py`

