#!/usr/bin/env python3
"""
run_guardian.py — End-to-end CLI for the CANDELA governance framework.

Point it at a document, pick a mode, get a verdict.

Usage:
  python run_guardian.py --input document.pdf --mode strict
  python run_guardian.py --input document.txt --mode regex_only
  python run_guardian.py --input document.pdf --all-modes
  python run_guardian.py --input document.pdf --all-modes --output-json report.json

Modes:
  strict      Regex + MiniLM semantic blocking (synchronous). Most thorough.
  sync_light  Regex blocks immediately; semantic runs in background thread.
  regex_only  Regex patterns only. Fastest, no ML model loaded.

Requires: PyYAML, sentence-transformers, torch (for strict/sync_light)
Optional: pdfplumber or pypdf (for PDF input)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import socket
import subprocess
import sys
import time
from pathlib import Path

# ── ensure CWD is project root (paths in guardian_runtime are relative) ──
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)
sys.path.insert(0, str(SCRIPT_DIR))

MODES = ("strict", "sync_light", "regex_only")

def _host_resolves(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False

def _resolve_ruleset_arg(arg: str | None) -> Path:
    """
    Resolve a reviewer-friendly ruleset selector.

    Default is the canonical baseline: src/directives_schema.json
    Optional packs live in ./rulesets/.
    """
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

def _configure_hf_offline(offline: bool) -> None:
    # Keep the CLI clean when DNS/network is unavailable.
    # If the model is not cached, strict/sync_light will fail with a clear message.
    if offline:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

def _ru_maxrss_bytes() -> int:
    # ru_maxrss units differ by OS:
    # - macOS: bytes
    # - Linux: kilobytes
    v = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(v)
    return int(v) * 1024


# ── text extraction ─────────────────────────────────────────────────────
def extract_text(filepath: Path) -> str:
    """Extract plain text from PDF, .txt, or .md files."""
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(str(filepath)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages)
        except ImportError:
            pass
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(filepath))
            pages = [p.extract_text() or "" for p in reader.pages]
            return "\n".join(pages)
        except ImportError:
            print("ERROR: PDF support requires pdfplumber or pypdf.")
            print("  pip install pdfplumber   (recommended)")
            print("  pip install pypdf")
            sys.exit(1)
    else:
        return filepath.read_text(encoding="utf-8")


# ── directive bundle hash ───────────────────────────────────────────────
def _hash_is_recorded_in_anchors(digest: str) -> bool:
    anchors = SCRIPT_DIR / "docs" / "ANCHORS.md"
    if not anchors.exists():
        return False
    return f"`{digest}`" in anchors.read_text(encoding="utf-8")

def compute_bundle_hash(ruleset_path: Path) -> dict:
    """Load selected ruleset, compute canonical SHA-256, and check if it is logged in docs/ANCHORS.md."""
    with ruleset_path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    bundle_hash = hashlib.sha256(canonical.encode()).hexdigest()

    # Support both modern dict shape and legacy list shape.
    if isinstance(obj, dict) and isinstance(obj.get("directives"), list):
        directive_count = len(obj["directives"])
    elif isinstance(obj, list):
        directive_count = len(obj)
    else:
        directive_count = 0

    return {
        "ruleset_path": str(ruleset_path),
        "directive_bundle_hash": bundle_hash,
        "directive_count": directive_count,
        "hash_recorded_in_docs": _hash_is_recorded_in_anchors(bundle_hash),
    }


# ── merkle root of output log ──────────────────────────────────────────
def compute_merkle_root() -> dict | None:
    """Compute Merkle root over all lines in output_log.jsonl, if it exists."""
    log_file = SCRIPT_DIR / "logs" / "output_log.jsonl"
    if not log_file.exists():
        return None
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return None

    def merkle(hashes: list[bytes]) -> bytes:
        level = hashes
        while len(level) > 1:
            it = iter(level)
            nxt = []
            for a in it:
                b = next(it, a)
                nxt.append(hashlib.sha256(a + b).digest())
            level = nxt
        return level[0]

    def leaf(line: str) -> bytes:
        return hashlib.sha256(line.encode("utf-8")).digest()

    leaves = [leaf(l) for l in lines]
    return {
        "merkle_root": merkle(leaves).hex(),
        "log_entries": len(lines),
    }

def compute_merkle_root_for_lines(lines: list[str]) -> dict | None:
    """Compute Merkle root over provided JSONL lines (or return None if empty)."""
    if not lines:
        return None

    def leaf(line: str) -> bytes:
        return hashlib.sha256(line.encode("utf-8")).digest()

    def merkle(hashes: list[bytes]) -> bytes:
        level = hashes
        while len(level) > 1:
            it = iter(level)
            nxt = []
            for a in it:
                b = next(it, a)
                nxt.append(hashlib.sha256(a + b).digest())
            level = nxt
        return level[0]

    leaves = [leaf(l) for l in lines]
    return {"merkle_root": merkle(leaves).hex(), "log_entries": len(lines)}

def maybe_anchor_outputs(allow_anchor: bool) -> dict | None:
    """
    Optionally anchor recent outputs to Sepolia by calling src/anchor_outputs.py.
    Returns a dict with stdout on success; returns None if not requested.
    """
    if not allow_anchor:
        return None

    # Avoid partial failures and keep reviewer UX crisp.
    rpc = os.getenv("SEPOLIA_RPC_URL")
    key = os.getenv("PRIVATE_KEY") or os.getenv("SEPOLIA_PRIVATE_KEY")
    if not rpc or not key:
        print("NOTE: Skipping on-chain output anchoring (missing SEPOLIA_RPC_URL and/or PRIVATE_KEY in .env).")
        return {"anchored": False, "reason": "missing_env"}

    print("Anchoring output log batch on Sepolia (Merkle root)...")
    proc = subprocess.run(
        [sys.executable, "src/anchor_outputs.py"],
        capture_output=True,
        text=True,
        cwd=str(SCRIPT_DIR),
    )
    if proc.returncode != 0:
        print("ERROR: Output anchoring failed.")
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print(proc.stderr.strip())
        return {"anchored": False, "reason": "anchor_failed", "stdout": proc.stdout, "stderr": proc.stderr}
    if proc.stdout:
        print(proc.stdout.strip())
    return {"anchored": True, "stdout": proc.stdout, "stderr": proc.stderr}


# ── single-mode run ────────────────────────────────────────────────────
def run_one_mode(text: str, mode: str) -> dict:
    """
    Run guardian_chat() in the specified mode.
    Returns verdict + resource metrics.
    """
    try:
        import src.guardian_runtime as rt
    except Exception as e:
        # Most common failure: semantic model cannot be fetched and is not cached.
        msg = str(e)
        if "HF_HUB_OFFLINE" in os.environ or "TRANSFORMERS_OFFLINE" in os.environ:
            msg = (
                "Semantic model unavailable in offline mode. "
                "Either run once with internet to cache the model, or use --mode regex_only."
            )
        return {
            "mode": mode,
            "passed": False,
            "score": 0,
            "violations": ["runtime_import_failed"],
            "notes": [msg],
            "wall_time_ms": 0.0,
            "cpu_time_ms": 0.0,
            "mem_rss_kb": 0,
            "mem_delta_kb": 0,
        }

    # override mode at module level
    rt.MODE = mode
    if mode == "regex_only":
        rt.SEM_ENABLED = False
    else:
        rt.SEM_ENABLED = bool(
            rt.CFG.get("detectors", {})
            .get("mini_semantic", {})
            .get("enabled", True)
        )

    # clear cache so each mode gets a fresh run
    rt._cache.clear()

    mem_before_b = _ru_maxrss_bytes()
    t_wall = time.perf_counter()
    t_cpu = time.process_time()

    result = rt.guardian_chat(text)

    wall_ms = (time.perf_counter() - t_wall) * 1_000
    cpu_ms = (time.process_time() - t_cpu) * 1_000
    mem_after_b = _ru_maxrss_bytes()
    mem_after_kb = int(mem_after_b // 1024)
    mem_delta_kb = int((mem_after_b - mem_before_b) // 1024)

    return {
        "mode": mode,
        "passed": result.get("passed", False),
        "score": result.get("score", 0),
        "violations": result.get("violations", []),
        "notes": result.get("notes", []),
        "wall_time_ms": round(wall_ms, 2),
        "cpu_time_ms": round(cpu_ms, 2),
        "mem_rss_kb": mem_after_kb,
        "mem_delta_kb": mem_delta_kb,
    }


# ── report printing ────────────────────────────────────────────────────
def print_header(input_path: str, text_len: int, text_hash: str):
    print("=" * 70)
    print("  CANDELA Guardian — End-to-End Run")
    print("=" * 70)
    print(f"  Input:       {input_path}")
    print(f"  Text length: {text_len:,} characters")
    print(f"  Text SHA256: {text_hash}")
    print()


def print_bundle_info(info: dict):
    print("── Directive Bundle ──────────────────────────────────────────")
    print(f"  Ruleset path:      {info['ruleset_path']}")
    print(f"  Directives loaded: {info['directive_count']}")
    print(f"  Bundle SHA-256:    {info['directive_bundle_hash']}")
    recorded = "YES" if info["hash_recorded_in_docs"] else "NO"
    print(f"  Hash in ANCHORS.md:{recorded}")
    print()


def print_mode_result(r: dict):
    status = "PASS" if r["passed"] else "FAIL"
    print(f"── Mode: {r['mode']:<12} ── Result: {status} ─────────────────────")
    print(f"  Score:      {r['score']}")
    print(f"  Violations: {len(r['violations'])}", end="")
    if r["violations"]:
        print(f"  [{', '.join(r['violations'])}]")
    else:
        print()
    if r["notes"]:
        print(f"  Notes:      {r['notes']}")
    print(f"  Wall time:  {r['wall_time_ms']:>10.2f} ms")
    print(f"  CPU time:   {r['cpu_time_ms']:>10.2f} ms")
    print(f"  RSS memory: {r['mem_rss_kb']:>10,} KB")
    if r["mem_delta_kb"] > 0:
        print(f"  RSS delta:  +{r['mem_delta_kb']:>9,} KB")
    print()


def print_merkle_info(info: dict | None):
    print("── Output Log / Merkle ──────────────────────────────────────")
    if info is None:
        print("  No output log yet.")
    else:
        print(f"  Log entries:  {info['log_entries']}")
        print(f"  Merkle root:  {info['merkle_root']}")
    print()


def print_footer():
    print("=" * 70)
    print("  Run complete.")
    print("=" * 70)


# ── main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Run the CANDELA Guardian framework against a document.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input file (PDF, .txt, .md)",
    )
    parser.add_argument(
        "--mode", "-m", choices=MODES, default=None,
        help="Execution mode (default: strict)",
    )
    parser.add_argument(
        "--all-modes", action="store_true",
        help="Run all three modes sequentially for comparison",
    )
    parser.add_argument(
        "--output-json", "-o", default=None,
        help="Write machine-readable JSON report to this path",
    )
    parser.add_argument(
        "--offline", action="store_true",
        help="Force offline mode (prevents Hugging Face network calls; requires cached model for semantic modes)",
    )
    parser.add_argument(
        "--anchor-outputs", action="store_true",
        help="Anchor the output log batch on Sepolia (Merkle root). Requires .env with SEPOLIA_RPC_URL and PRIVATE_KEY.",
    )
    parser.add_argument(
        "--ruleset", default="baseline",
        help=(
            "Ruleset selector (optional). "
            "Use baseline (default), security_hardening, privacy_strict, or a file path."
        ),
    )
    args = parser.parse_args()

    if not args.all_modes and args.mode is None:
        args.mode = "strict"

    # Configure Hugging Face offline behavior before importing any runtime modules.
    auto_offline = not _host_resolves("huggingface.co")
    offline = bool(args.offline or auto_offline)
    _configure_hf_offline(offline)

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    ruleset_path = _resolve_ruleset_arg(args.ruleset)
    if not ruleset_path.exists():
        print(f"ERROR: Ruleset not found: {ruleset_path}")
        sys.exit(1)
    # Set once before runtime import (guardian_runtime reads this at import time).
    os.environ["CANDELA_RULESET_PATH"] = str(ruleset_path)

    # ── extract text ──
    print(f"\nExtracting text from {input_path.name} ...")
    t0 = time.perf_counter()
    text = extract_text(input_path)
    extract_ms = (time.perf_counter() - t0) * 1_000
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    print(f"  Done ({extract_ms:.0f} ms, {len(text):,} chars)\n")

    # ── bundle hash ──
    bundle_info = compute_bundle_hash(ruleset_path)

    # ── print header ──
    print_header(str(input_path), len(text), text_hash)
    print_bundle_info(bundle_info)

    # Track how many output log entries exist before this run (so we can report the delta).
    log_file = SCRIPT_DIR / "logs" / "output_log.jsonl"
    before_lines = log_file.read_text(encoding="utf-8").splitlines() if log_file.exists() else []

    # ── run modes ──
    modes_to_run = list(MODES) if args.all_modes else [args.mode]
    results = []
    for mode in modes_to_run:
        print(f"Running mode: {mode} ...")
        r = run_one_mode(text, mode)
        results.append(r)
        print_mode_result(r)

    # ── merkle root (after runs, so log entries exist) ──
    merkle_info = compute_merkle_root()
    after_lines = log_file.read_text(encoding="utf-8").splitlines() if log_file.exists() else []
    delta_lines = after_lines[len(before_lines):] if len(after_lines) >= len(before_lines) else []
    merkle_delta = compute_merkle_root_for_lines(delta_lines)
    print_merkle_info(merkle_info)
    if merkle_delta is not None:
        print("── This Run Only (Delta) ─────────────────────────────────")
        print(f"  New log entries: {merkle_delta['log_entries']}")
        print(f"  Merkle root:     {merkle_delta['merkle_root']}")
        print()

    print_footer()

    anchor_result = maybe_anchor_outputs(args.anchor_outputs)

    # ── JSON report ──
    if args.output_json:
        report = {
            "input": str(input_path),
            "text_length": len(text),
            "text_sha256": text_hash,
            "extraction_ms": round(extract_ms, 2),
            "offline": offline,
            "directive_bundle": bundle_info,
            "results": results,
            "merkle": merkle_info,
            "merkle_delta": merkle_delta,
            "anchor_outputs": anchor_result,
        }
        out_path = Path(args.output_json)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\nJSON report written to: {out_path}")


if __name__ == "__main__":
    main()
