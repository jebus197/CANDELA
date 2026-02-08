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
import sys
import time
from pathlib import Path

# ── ensure CWD is project root (paths in guardian_runtime are relative) ──
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)
sys.path.insert(0, str(SCRIPT_DIR))

CANONICAL_HASH = "7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d"
MODES = ("strict", "sync_light", "regex_only")

def _host_resolves(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False

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
def compute_bundle_hash() -> dict:
    """Load directives, compute SHA-256 bundle hash, check canonical match."""
    schema_path = SCRIPT_DIR / "src" / "directives_schema.json"
    with schema_path.open("r", encoding="utf-8") as f:
        directives = json.load(f)
    canonical = json.dumps(directives, sort_keys=True, ensure_ascii=False)
    bundle_hash = hashlib.sha256(canonical.encode()).hexdigest()
    return {
        "directive_bundle_hash": bundle_hash,
        "directive_count": len(directives),
        "canonical_match": bundle_hash == CANONICAL_HASH,
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
    return {
        "merkle_root": merkle(leaves).hex(),
        "log_entries": len(lines),
    }


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
    print(f"  Directives loaded: {info['directive_count']}")
    print(f"  Bundle SHA-256:    {info['directive_bundle_hash']}")
    match = "YES" if info["canonical_match"] else "NO — MISMATCH"
    print(f"  Canonical match:   {match}")
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

    # ── extract text ──
    print(f"\nExtracting text from {input_path.name} ...")
    t0 = time.perf_counter()
    text = extract_text(input_path)
    extract_ms = (time.perf_counter() - t0) * 1_000
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    print(f"  Done ({extract_ms:.0f} ms, {len(text):,} chars)\n")

    # ── bundle hash ──
    bundle_info = compute_bundle_hash()

    # ── print header ──
    print_header(str(input_path), len(text), text_hash)
    print_bundle_info(bundle_info)

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
    print_merkle_info(merkle_info)

    print_footer()

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
        }
        out_path = Path(args.output_json)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\nJSON report written to: {out_path}")


if __name__ == "__main__":
    main()
