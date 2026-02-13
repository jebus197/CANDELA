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
import hashlib
import os
import socket
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

def _host_resolves(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False

def _configure_offline_env(offline: bool) -> None:
    # Keep console output clean when DNS/network is unavailable.
    # If models are not cached, generation or semantic checks may fail with clear messages.
    if offline:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


def _best_device() -> str:
    """Pick the fastest available device: MPS (Apple Silicon GPU) > CPU."""
    try:
        import torch
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


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

    device = _best_device()
    print(f"Using device: {device}")

    tok = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True, use_fast=True)
    mdl = AutoModelForCausalLM.from_pretrained(str(model_dir), local_files_only=True)
    mdl.to(device)
    mdl.eval()
    return tok, mdl


def _generate(tok, mdl, prompt: str, max_new_tokens: int, temperature: float) -> str:
    import torch

    device = str(mdl.device)
    inputs = tok(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
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

def _read_log_lines() -> list[str]:
    p = SCRIPT_DIR / "logs" / "output_log.jsonl"
    if not p.exists():
        return []
    return p.read_text(encoding="utf-8").splitlines()

def _merkle_root_for_lines(lines: list[str]) -> str | None:
    if not lines:
        return None
    level = [hashlib.sha256(ln.encode("utf-8")).digest() for ln in lines]
    while len(level) > 1:
        it = iter(level)
        nxt = []
        for a in it:
            b = next(it, a)
            nxt.append(hashlib.sha256(a + b).digest())
        level = nxt
    return level[0].hex()

def _maybe_periodic_anchor(
    *,
    enable: bool,
    every_n: int,
    interval_s: int,
    outputs_seen: int,
    last_anchor_ts: float | None,
) -> float | None:
    if not enable:
        return last_anchor_ts
    now = time.time()
    due_by_count = every_n > 0 and outputs_seen > 0 and outputs_seen % every_n == 0
    due_by_time = interval_s > 0 and (last_anchor_ts is None or (now - last_anchor_ts) >= interval_s)
    if due_by_count or due_by_time:
        _anchor_outputs_if_requested(True)
        return now
    return last_anchor_ts


def main() -> None:
    p = argparse.ArgumentParser(description="Generate text with a local model, then run CANDELA on it.")
    p.add_argument("--prompt", required=True, help="Prompt to generate from.")
    p.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR), help="Local model directory (default: models/TinyLlama-1.1B-Chat-v1.0).")
    p.add_argument("--mode", choices=MODES, default=None, help="CANDELA mode (default: strict).")
    p.add_argument("--all-modes", action="store_true", help="Run strict, sync_light, and regex_only.")
    p.add_argument("--interactive", action="store_true", help="Interactive loop: keep prompting until you type 'exit'.")
    p.add_argument("--turns", type=int, default=0, help="Max turns in interactive mode (0 = unlimited).")
    p.add_argument("--max-new-tokens", type=int, default=256, help="Generation length cap.")
    p.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature (0 disables sampling).")
    p.add_argument("--anchor-outputs", action="store_true", help="Anchor output log batch on Sepolia (requires .env creds).")
    p.add_argument("--anchor-every", type=int, default=0, help="If anchoring is enabled, anchor every N outputs (0 disables).")
    p.add_argument("--anchor-interval-min", type=int, default=0, help="If anchoring is enabled, anchor at most once per T minutes (0 disables).")
    p.add_argument("--max-print-chars", type=int, default=4000, help="Max characters of model output to print.")
    p.add_argument("--show-blocked", action="store_true", help="Print blocked model output too (demo only).")
    p.add_argument(
        "--ruleset",
        default="baseline",
        help="Ruleset selector (optional). Use baseline (default), security_hardening, privacy_strict, or a file path.",
    )
    args = p.parse_args()

    # Resolve ruleset selector and set env before importing CANDELA runtime.
    def _resolve_ruleset_arg(arg: str | None) -> Path:
        if not arg or arg.strip().lower() in ("baseline", "default"):
            return (SCRIPT_DIR / "src" / "directives_schema.json").resolve()
        a = arg.strip()
        low = a.lower()
        if low in ("security", "security_hardening"):
            return (SCRIPT_DIR / "rulesets" / "security_hardening.json").resolve()
        if low in ("privacy", "privacy_strict"):
            return (SCRIPT_DIR / "rulesets" / "privacy_strict.json").resolve()
        if low in ("health", "health_privacy", "health_privacy_micro"):
            return (SCRIPT_DIR / "rulesets" / "health_privacy_micro.json").resolve()
        p = Path(a).expanduser()
        if not p.is_absolute():
            p = (SCRIPT_DIR / p).resolve()
        return p

    ruleset_path = _resolve_ruleset_arg(args.ruleset)
    if not ruleset_path.exists():
        _die(f"Ruleset not found: {ruleset_path}")
    os.environ["CANDELA_RULESET_PATH"] = str(ruleset_path)

    mode = "strict" if (not args.all_modes and args.mode is None) else args.mode
    modes = list(MODES) if args.all_modes else [mode]

    offline = not _host_resolves("huggingface.co")
    _configure_offline_env(offline)

    model_dir = Path(args.model_dir).expanduser().resolve()

    print("Loading local model...")
    tok, mdl = _load_local_text_model(model_dir)
    print(f"Model dir: {model_dir}")

    outputs_seen = 0
    last_anchor_ts: float | None = None
    interval_s = max(0, int(args.anchor_interval_min)) * 60

    def _one_turn(user_prompt: str) -> None:
        nonlocal outputs_seen, last_anchor_ts
        before = _read_log_lines()

        print("\nGenerating output...")
        generated = _generate(tok, mdl, user_prompt, args.max_new_tokens, args.temperature)
        outputs_seen += 1

        # Run CANDELA first. Only show model output if it passes (or show-blocked is set).
        verdicts = []
        for m in modes:
            verdicts.append(_run_candela(generated, m))

        print("\n=== CANDELA Verdicts ===\n")
        any_block = False
        for v in verdicts:
            status = "PASS" if v.get("passed") else "FAIL"
            notes = v.get("notes") or []
            viols = v.get("violations") or []
            print(f"- mode={v['mode']} result={status} wall={v.get('wall_time_ms')}ms violations={len(viols)}")
            if viols:
                print(f"  violations: {viols}")
            if notes:
                print(f"  notes: {notes}")
            if not v.get("passed"):
                any_block = True

        if (not any_block) or args.show_blocked:
            out = generated
            if len(out) > args.max_print_chars:
                out = out[: args.max_print_chars] + "\n\n[...truncated...]\n"
            print("\n=== Model Output ===\n")
            print(out)
        else:
            print("\n(Model output blocked; use --show-blocked to print it for demo purposes.)\n")

        after = _read_log_lines()
        delta = after[len(before):] if len(after) >= len(before) else []
        root = _merkle_root_for_lines(delta)
        if root:
            print("=== Audit Log (This Turn) ===")
            print(f"New log entries: {len(delta)}")
            print(f"Delta Merkle root: {root}")
            print()

        # Periodic anchoring (optional)
        last_anchor_ts = _maybe_periodic_anchor(
            enable=bool(args.anchor_outputs),
            every_n=int(args.anchor_every),
            interval_s=interval_s,
            outputs_seen=outputs_seen,
            last_anchor_ts=last_anchor_ts,
        )

    if args.interactive:
        print("\nInteractive mode: type your prompt and press Enter. Type 'exit' to stop.\n")
        turns_left = int(args.turns)
        while True:
            if turns_left == 0 and args.turns > 0:
                break
            try:
                user_prompt = input("You> ").strip()
            except EOFError:
                break
            if not user_prompt:
                continue
            if user_prompt.lower() in ("exit", "quit"):
                break
            _one_turn(user_prompt)
            if args.turns > 0:
                turns_left -= 1
    else:
        _one_turn(args.prompt)

    # Always allow a final anchor at exit if anchoring is enabled and periodic triggers never fired.
    if args.anchor_outputs and (args.anchor_every == 0 and args.anchor_interval_min == 0):
        _anchor_outputs_if_requested(True)


if __name__ == "__main__":
    main()
