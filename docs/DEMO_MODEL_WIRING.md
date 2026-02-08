# Demo Model Wiring (Reviewer-Friendly)

This is an optional demo that shows CANDELA actively checking a model's output:

1. A small local model generates text from a prompt.
2. CANDELA checks that generated text (strict / sync_light / regex_only).
3. CANDELA writes a local audit log entry to `logs/output_log.jsonl`.
4. (Optional) CANDELA anchors a Merkle root of the output log batch on Sepolia.

This keeps the demo simple and avoids "you must know the internals" reviewer friction.

## Recommended demo model (CPU-friendly)

Model identifier: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`

Why:
- Small and widely used for quick local testing.
- Runs on CPU (slowly, but it works on ordinary machines).

## One-time install (demo only)

This demo script uses `transformers` for local generation. It is intentionally not part
of the core CANDELA dependencies.

Install:

```bash
python3 -m pip install transformers
```

## Download the model locally

For this demo, the model must be present on disk (no network required at runtime).

Place the model snapshot folder at:

`./models/TinyLlama-1.1B-Chat-v1.0/`

This should contain the usual model files (config + tokenizer + weights).

## Run the demo

From the CANDELA repo root:

```bash
python3 demo_model_guardian.py --prompt "Explain what a Merkle root is in one paragraph." --mode strict
```

To compare all modes:

```bash
python3 demo_model_guardian.py --prompt "Summarise CANDELA in 5 bullet points." --all-modes
```

Optional: anchor outputs (requires a local `.env` configured for Sepolia):

```bash
python3 demo_model_guardian.py --prompt "Summarise CANDELA in 5 bullet points." --all-modes --anchor-outputs
```

## What to look for

- The script prints the model's raw generated output.
- It prints CANDELA PASS/FAIL for each selected mode.
- It appends a record to `logs/output_log.jsonl`.
- If `--anchor-outputs` is used and credentials exist, it anchors a Merkle root via `src/anchor_outputs.py`.
