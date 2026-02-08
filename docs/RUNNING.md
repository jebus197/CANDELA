# Running CANDELA (Reviewer Guide)

This is the single "how to run it" guide for CANDELA.

If you only do one thing: run `run_guardian.py` against a file and read the PASS/FAIL output.

## 1) Install dependencies

From the CANDELA folder:

```bash
python3 -m pip install -r requirements.txt
```

Note: this installs `torch` and `sentence-transformers` (larger downloads).

Optional (only needed for PDF input):

```bash
python3 -m pip install pdfplumber
```

If `pdfplumber` fails, use:

```bash
python3 -m pip install pypdf
```

## 2) Run the Guardian on a file

Text / Markdown:

```bash
python3 run_guardian.py --input path/to/file.txt --mode strict
python3 run_guardian.py --input path/to/file.md  --mode regex_only
```

PDF:

```bash
python3 run_guardian.py --input path/to/file.pdf --mode strict
```

## 3) Modes (what they mean)

- `strict`
  - Most thorough. Runs deterministic checks and waits for the semantic (MiniLM) checks.
- `sync_light`
  - Fastest "full" mode. Runs deterministic checks immediately; semantic checks run in the background.
- `regex_only`
  - Deterministic checks only. Fastest, and does not load the ML model.

## 4) Optional demo ruleset packs (keep first run simple)

Default ruleset (no flag needed):
- baseline: `src/directives_schema.json`

Optional packs (only if you want to explore):
- `security_hardening` -> `rulesets/security_hardening.json`
- `privacy_strict` -> `rulesets/privacy_strict.json`

Examples:

```bash
python3 run_guardian.py --input path/to/file.pdf --mode strict --ruleset security_hardening
python3 run_guardian.py --input path/to/file.pdf --mode strict --ruleset privacy_strict
```

PoC note: optional packs are intentionally opt-in so reviewers are not forced into a multiple-choice setup step before the demo works.

## 5) Save a machine-readable report (JSON)

```bash
python3 run_guardian.py --input path/to/file.pdf --all-modes --output-json report.json
```

## 6) Optional anchoring (tamper-evident receipts)

There are two kinds of anchoring:

1) Ruleset anchoring (hash of the ruleset JSON)
- `docs/ANCHORS.md` lists the ruleset hashes that have been anchored on Sepolia.
- The baseline ruleset is intended to be the default, anchored "rules in force".
- Optional packs can be anchored too if you want the same provenance for a specific demo run.

Anchor a ruleset (default is baseline):

```bash
python3 src/anchor_hash.py
```

Anchor a specific pack:

```bash
python3 src/anchor_hash.py --path rulesets/security_hardening.json
```

2) Output anchoring (Merkle root of local output log lines)
- CANDELA logs each checked output to `./logs/output_log.jsonl`.
- `src/anchor_outputs.py` batches new log lines into a Merkle root and anchors only the root on Sepolia.

To anchor new output log entries after running a check:

```bash
python3 src/anchor_outputs.py
```

## 7) Optional: model integration demo (active monitoring)

If you want to see CANDELA monitoring generated model output in real time, use:
- `docs/MODEL_INTEGRATION.md`

