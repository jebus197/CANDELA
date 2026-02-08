#!/usr/bin/env python3
"""
demo_model_guardian.py

Reviewer-friendly demo: generate text with a small local model and run CANDELA on it.

This script is intentionally "thin glue" (no new abstractions). It:
1) Loads a local model from ./models/<model-name> (no network required).
2) Generates output from a prompt.
3) Runs CANDELA (strict / sync_light / regex_only) over that generated output.
4) Writes the usual local audit log entry (logs/output_log.jsonl).
5) Optionally anchors the output log batch on Sepolia (Merkle root) if requested.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)
sys.path.insert(0, str(SCRIPT_DIR))

MODES = ("strict", "sync_light", "regex_only")
DEFAULT_MODEL_DIR = SCRIPT_DIR / "models" / "TinyLlama-1.1B-Chat-v1.0"


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(code)


def _load_local_text_model(model_dir: Path):
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception:
        _die("Missing dependency: transformers. Install with: python3 -m pip install transformers")

    if not model_dir.exists():
        _die(
            f"Model directory not found: {model_dir}\n"
            "Place a small model snapshot folder there and retry.\n"
            "Expected: model config + tokenizer + weights (downloaded from your chosen model host)."
        )

    tok = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True, use_fast=True)
    mdl = AutoModelForCausalLM.from_pretrained(str(model_dir), local_files_only=True)
    return tok, mdl


def _generate(tok, mdl, prompt: str, max_new_tokens: int, temperature: float) -> str:
    import torch

    inputs = tok(prompt, return_tensors="pt")
    # CPU-only by default for reviewer machines.
    mdl.to("cpu")
    with torch.no_grad():
        out = mdl.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0.0,
            temperature=max(temperature, 1e-6),
        )
    return tok.decode(out[0], skip_special_tokens=True)


def _run_candela(text: str, mode: str) -> dict:
    # Import here to avoid pulling CANDELA runtime unless needed.
    import src.guardian_runtime as rt

    rt.MODE = mode
    if mode == "regex_only":
        rt.SEM_ENABLED = False
    else:
        rt.SEM_ENABLED = bool(rt.CFG.get("detectors", {}).get("mini_semantic", {}).get("enabled", True))

    t0 = time.perf_counter()
    verdict = rt.guardian_chat(text)
    dt_ms = (time.perf_counter() - t0) * 1_000
    verdict = dict(verdict)
    verdict["mode"] = mode
    verdict["wall_time_ms"] = round(dt_ms, 2)
    return verdict


def _anchor_outputs_if_requested(anchor: bool) -> None:
    if not anchor:
        return

    rpc = os.getenv("SEPOLIA_RPC_URL")
    key = os.getenv("PRIVATE_KEY") or os.getenv("SEPOLIA_PRIVATE_KEY")
    if not rpc or not key:
        print("NOTE: Skipping anchoring (missing SEPOLIA_RPC_URL and/or PRIVATE_KEY in .env).")
        return

    print("Anchoring output log batch on Sepolia (Merkle root)...")
    proc = subprocess.run([sys.executable, "src/anchor_outputs.py"], capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    if proc.returncode != 0:
        print("ERROR: anchoring failed.")
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print(proc.stderr.strip())
        raise SystemExit(proc.returncode)
    if proc.stdout:
        print(proc.stdout.strip())


def main() -> None:
    p = argparse.ArgumentParser(description="Generate text with a local model, then run CANDELA on it.")
    p.add_argument("--prompt", required=True, help="Prompt to generate from.")
    p.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR), help="Local model directory (default: models/TinyLlama-1.1B-Chat-v1.0).")
    p.add_argument("--mode", choices=MODES, default=None, help="CANDELA mode (default: strict).")
    p.add_argument("--all-modes", action="store_true", help="Run strict, sync_light, and regex_only.")
    p.add_argument("--max-new-tokens", type=int, default=256, help="Generation length cap.")
    p.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature (0 disables sampling).")
    p.add_argument("--anchor-outputs", action="store_true", help="Anchor output log batch on Sepolia (requires .env creds).")
    args = p.parse_args()

    mode = "strict" if (not args.all_modes and args.mode is None) else args.mode
    modes = list(MODES) if args.all_modes else [mode]

    model_dir = Path(args.model_dir).expanduser().resolve()

    print("Loading local model...")
    tok, mdl = _load_local_text_model(model_dir)
    print(f"Model dir: {model_dir}")

    print("\nGenerating output...")
    generated = _generate(tok, mdl, args.prompt, args.max_new_tokens, args.temperature)

    print("\n=== Model Output (raw) ===\n")
    print(generated)
    print("\n=== CANDELA Verdicts ===\n")

    for m in modes:
        v = _run_candela(generated, m)
        status = "PASS" if v.get("passed") else "FAIL"
        notes = v.get("notes") or []
        viols = v.get("violations") or []
        print(f"- mode={m} result={status} wall={v.get('wall_time_ms')}ms violations={len(viols)}")
        if viols:
            print(f"  violations: {viols}")
        if notes:
            print(f"  notes: {notes}")

    _anchor_outputs_if_requested(args.anchor_outputs)


if __name__ == "__main__":
    main()

