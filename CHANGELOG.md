# CANDELA – Change Log
All notable changes to this project are documented here.

## [v0.1-poc] – 2025-05-14
### Added
- Functional PoC: `guardian_prototype.py` + directive hashing (`anchor_hash.py`).
- `directives_schema.json` (76 directives) anchored on Sepolia testnet.
### Notes
- Tag **v0.1-poc** and branch **backup/poc_v0.1** mark the immutable baseline.

## [v0.3] – 2026-02-06
### Added
- Canonical anchoring completed on Sepolia (hash + tx recorded).
- bots.md coordination file for human/LLM handoff.
- Output provenance: append-only output log, Merkle batching, and on-chain anchoring via `src/anchor_outputs.py`.
### Changed
- Documentation aligned to v0.3 (Tech Spec + Quick-Start).
- Provenance references updated to canonical hash/tx.
- README wording/UX notes; roadmap phases updated.
- requirements.txt pinned torch for semantic guard.
### Removed
- Duplicate Mini‑BERT files (`src/mini_semantic.py`, `src/src/detectors/mini_semantic.py`).

## [Unreleased]
### Planned
- Service/API hardening, proof/verify helper CLI, CI/CD and pilot readiness.
