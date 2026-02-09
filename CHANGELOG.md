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
- Duplicate semantic detector files removed (MiniLM / `all-MiniLM-L6-v2`).

## [Unreleased]
### Added
- Reviewer checklist and verification flow: `docs/REVIEWER_CHECKLIST.md` and `scripts/candela_demo.py`.
- End-to-end CLI runner: `run_guardian.py` (modes, JSON report output).
- Optional demo ruleset packs under `rulesets/` plus `--ruleset` selection.
- Output provenance tooling: `src/verify_output.py`, `src/latency_stats.py`, Merkle batching/anchoring via `src/anchor_outputs.py`.

### Changed
- Output anchoring CLI hardened: `src/anchor_outputs.py` supports `--dry-run` and safe `--help` (no surprise network calls).

### Planned
- Service/API hardening, CI/CD, and pilot readiness.
