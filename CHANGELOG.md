# CANDELA – Change Log
All notable changes to this project are documented here.

## [v0.1-poc] – 2025-05-14
### Added
- Functional PoC: `guardian_prototype.py` + directive hashing (`anchor_hash.py`).
- `directives_schema.json` (76 directives) anchored on Sepolia testnet.
### Notes
- Tag **v0.1-poc** and branch **backup/poc_v0.1** mark the immutable baseline.

## [Unreleased]
### Added
- Validation helpers merged into `guardian_extended.py`.
- FastAPI wrapper `src/api/guardian_api.py`.
 - Mini‑BERT semantic guard wired into runtime cache path.
 - Anchoring script hardened (SHA‑256, env validation, safe log append).
### Changed
- `requirements.txt` adds `fastapi`, `uvicorn`, `pydantic`.
 - Directive hash constants aligned across runtime and tests.
 - Guardian API wiring and return shape.
### Removed
- Legacy file `src/guardian_poc_v0.1.py`.
 - Duplicate Mini‑BERT files (`src/mini_semantic.py`, `src/src/detectors/mini_semantic.py`).

## [v0.3] – 2026-02-03
### Added
- Canonical anchoring completed on Sepolia (hash + tx recorded).
- bots.md coordination file for human/LLM handoff.
### Changed
- Documentation aligned to v0.3 (Tech Spec + Quick-Start).
- Provenance references updated to canonical hash/tx.
