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
### Changed
- `requirements.txt` adds `fastapi`, `uvicorn`, `pydantic`.
### Removed
- Legacy file `src/guardian_poc_v0.1.py`.
