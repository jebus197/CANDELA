# Reviewer Verification Checklist (CANDELA v0.3)

This checklist is designed for busy, sceptical reviewers.

Goal: verify what CANDELA *actually does today* (and what it does not claim to do).

## Fast path (5 minutes)

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Run tests (integrity sanity check):

```bash
python3 -m pytest -v
```

Expected: all tests pass.

3. Run the reviewer demo (recommended):

```bash
python3 scripts/candela_demo.py --no-interactive --mode regex_only
```

Expected:
- A clear PASS/FAIL verdict
- A printed SHA-256 for the active ruleset
- A note saying whether that hash is recorded in `docs/ANCHORS.md`
- Local audit logs written under `logs/`

## What CANDELA proves (today)

1. A ruleset can be expressed as machine-checkable policy-as-code
- Canonical baseline ruleset: `src/directives_schema.json`
- Exact directive inventory: `python3 src/report_directives.py`

2. The Guardian enforces that ruleset at runtime
- Deterministic checks: `src/directive_validation.py`
- Semantic checks (optional): `src/detectors/mini_semantic.py`
- Runtime glue and modes: `src/guardian_runtime.py`

3. You can produce a tamper-evident audit trail
- Off-chain: append-only log lines in `logs/output_log.jsonl`
- Optional on-chain receipts: Merkle-root output anchoring via `src/anchor_outputs.py`

## What CANDELA does NOT claim (today)

- It does not claim access to any vendor system prompts.
- It does not claim you can “install CANDELA into” a closed model without vendor cooperation.
- It does not claim production readiness (security review, hardening, and operational controls are future work).

## Modes (what to expect)

- `regex_only`
  - Fastest. No ML model loaded.
  - Recommended for a first reviewer run.
- `strict`
  - Most thorough. Waits for semantic checks (MiniLM) when enabled.
  - First run can be slower (model load). Later runs should be faster (warm start / caching).
- `sync_light`
  - Returns quickly, while semantic checks run in the background.
  - Useful for high-throughput auditing, not “firewall-style” blocking.

To compare modes quickly:

```bash
python3 scripts/candela_demo.py --no-interactive --all-modes
```

## Optional anchoring (no drama path)

Anchoring is optional. The demo and tests work without it.

If you want to inspect output anchoring without sending any transaction:

```bash
python3 src/anchor_outputs.py --dry-run
```

Expected:
- “New entries: N (lines A-B)”
- “Merkle root: <hex>”
- “Dry run: no transaction sent.”

If you want on-chain receipts, you need:
- Sepolia test ETH (for gas)
- An RPC provider URL
- A private key

These are supplied locally via `.env` (and are intentionally git-ignored).

## Transparency: enforced vs aspirational

The primary reviewer risk in governance projects is “paper rules” that are not actually executed.

CANDELA addresses this directly:
- `docs/VALIDATION_COVERAGE.md` states exactly what is enforced for the default ruleset.
- `python3 src/report_directives.py` prints the exact directive count and IDs/titles.

## Known reviewer-relevant limitations (frank)

- Semantic checks require heavier dependencies (`torch`, `sentence-transformers`) and may be slow on first run.
- Offline reviewers may see `strict` mode fall back to deterministic checks if the semantic model is not cached.
- Anchoring depends on external infrastructure (RPC provider + network + faucet availability).

None of these affect the core claim:
the Guardian can enforce a readable, auditable ruleset and log verifiable evidence of what happened.

