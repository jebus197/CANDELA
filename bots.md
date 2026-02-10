# bots.md — CANDELA Agent Handoff (Canonical)

Created by: the primary developer agent, acting under George Jackson’s instructions.
Purpose: Provide a single, authoritative handoff file for any future bot or human maintainer.
Context: This file (bots.md) recognises that modern development often involves both humans and LLMs. This file exists to make that collaboration explicit and safe.
Non‑negotiable rule: If any bot or human edits CANDELA, **this file should be considered canonical and must be updated** to reflect any new work.

---

## Scope & intent
This file records:
- Who made which changes, and why.
- What remains outstanding.
- How other bots should behave (tone, constraints, approvals).
- How to avoid accidental drift in the project’s philosophical grounding.

This is the **canonical** coordination file. If there is a conflict between other notes and this file, follow this file.

---

## Current status
- Legacy personal ruleset (v3.2) has been retired from the repo to avoid reviewer confusion.
  - Archived copy: `/Users/georgejackson/Developer_Projects/Candela_Legacy_Directives_Schema_v3.2_2026-02-08.json`
- Canonical ruleset in the repo is now an enterprise-facing example pack:
  - File: `src/directives_schema.json` (Enterprise E1.0)
  - All directives are machine-checkable (BLOCK or WARN); no `N/A` criteria.
- Tests run locally: all pass, including the reviewer-facing ruleset integrity check.

---

## Delegation map
### Prose‑focused model (British English)
Files to edit only after reviewing current content and confirming with the user:
- README.md
- docs/PROJECT_BRIEF.md
- docs/FAQ.md
- docs/directives_README.md

Goals:
- Improve clarity and flow without changing technical meaning.
- Preserve the philosophical grounding.
- Ask the user before any major rewrites.
- Keep British English spelling in narrative sections.

### Technical model (precision first)
Files to edit:
- docs/Tech_Spec.md
- docs/ROADMAP.md
- CHANGELOG.md
- DEVELOPER_NOTES.md
- GETTING_Started.md
- All code and tests

Goals:
- Keep dependencies, hashes, and procedures consistent.
- Avoid narrative embellishment.
- Use standard technical conventions.

---

## Anchoring (must be completed)
- Add credentials to `.env` in the repo root:
  - SEPOLIA_RPC_URL
  - PRIVATE_KEY (or SEPOLIA_PRIVATE_KEY)
- Run: `python3 src/anchor_hash.py`
- Record the tx hash in docs/ANCHORS.md
- Update any docs that reference the ruleset hash to point reviewers to `docs/ANCHORS.md`

---


## Tokenised Quality Incentives (post‑v1) — Implementation sketch
- Define public score thresholds tied to directive compliance (e.g., 85/90/95).
- Require an evidence bundle: directive hash, score, violations, timestamp, signer, optional content hash.
- Establish human‑authorship proof (Phase 1.1) as a gate before any reward.
- Add a human‑in‑the‑loop review pool for borderline or high‑impact content.
- Start with off‑chain credits; migrate to ERC‑20 only after abuse testing.
- Add anti‑gaming controls: reputation weights, sampling audits, reviewer cross‑checks, rate limits.
- Add anti‑abuse controls: appeal flow, audit logs, and revocation.
- Pilot with a small, vetted cohort; publish results before scaling.

## Outstanding tasks (high priority)
1) Package PoC “run bundle” for reviewers.
2) Verify docs/ANCHORS.md and provenance references are consistent.
3) Prepare reviewer‑facing summary and test instructions.

---

## Spell‑check policy
- User inputs are spell‑checked and corrected **for internal tasking only**.
- Project files are not silently rewritten for spelling unless explicitly approved.

---

## Last update log
- 2026‑02‑03: Created by the primary developer agent; added delegation map and anchoring steps.
- 2026‑02‑09: Added reviewer-first demo UX (`scripts/candela_demo.py`) and a micro-directives optional pack (`rulesets/health_privacy_micro.json`). Updated docs to point reviewers to a single fast demo path and documented optional packs consistently.
