# bots.md — CANDELA Agent Handoff (Canonical)

Created by: Codex (GPT-5), acting under George Jackson’s instructions.
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

## Current status (sandbox)
- Programmatic fixes completed in sandbox (Guardian wiring, hash alignment, MiniLM semantic detector de-duplication).
- Tests and stress checks run; pass.
- Anchoring executed successfully. Canonical hash 7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d anchored on Sepolia tx 0x2653a983ce75c31de39ab4b53c01fada024aac170c2fc99b7845f8df4702db70.

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
- Add credentials to `.env` in the sandbox:
  - SEPOLIA_RPC_URL
  - PRIVATE_KEY (or SEPOLIA_PRIVATE_KEY)
- Run: `python3 src/anchor_hash.py`
- Record the tx hash in docs/ANCHORS.md
- Update docs/ROADMAP.md and docs/PROJECT_BRIEF.md with the new hash/tx

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
- 2026‑02‑03: Created by Codex; added delegation map and anchoring steps.
