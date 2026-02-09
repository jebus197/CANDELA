# Validation Coverage (Enterprise Ruleset E1.0)

This document exists for reviewers.

It answers one question plainly:

What rules are actually enforced by running code, versus what is merely described?

In the E1.0 ruleset, every directive is machine-checkable and executed by code.

## Canonical ruleset
- File: `src/directives_schema.json`
- Ruleset name/version: `CANDELA Enterprise Ruleset` / `E1.0`
- Canonical SHA-256 (sorted keys, Unicode preserved): `bddd2587745d1d86a4d14cf006025386a218e4550642ca236ca6b682125e3f6a`
- On-chain anchor log: `docs/ANCHORS.md`

Note: if the ruleset file changes, the hash changes. That is expected. The whole point is that you can prove which exact rules were in force.

## Counts (exact)
- Directive objects: 12
- BLOCK-tier directives: 9
- WARN-tier directives: 3
- Directives with `validation_criteria: N/A`: 0

## Enforcement (where the code lives)
- Deterministic (regex/Luhn/structure) checks:
  - Implemented in `src/directive_validation.py`
  - Called by `src/guardian_runtime.py`
- Semantic similarity checks (MiniLM):
  - Model wrapper: `src/detectors/mini_semantic.py`
  - Prohibited intent phrases and per-directive thresholds live in the anchored ruleset (`src/directives_schema.json`)

## What "WARN" means
WARN-tier directives are still enforced by code, but they do not block output by default.

They exist to:
- surface review flags (for humans)
- provide signals for scoring / future policies

## Reviewer takeaway
- The current default ruleset is intentionally small and enterprise-looking: it focuses on high-signal safety, security, and privacy checks.
- The framework is designed so organisations can evolve the ruleset and re-anchor the new hash without changing the Guardian runtime.

## Optional packs (demo-only)
CANDELA also ships optional ruleset packs under `rulesets/` to demonstrate extensibility.

- They are opt-in (so the first run stays simple).
- They are machine-checkable by the same validator (`src/directive_validation.py`).
- If you use a pack and want on-chain provenance for that exact pack snapshot, you can anchor it with:
  - `python3 src/anchor_hash.py --path rulesets/<pack>.json`
