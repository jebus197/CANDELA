#!/usr/bin/env python3
"""
candela_demo.py

Reviewer-first demo UX: "60 seconds to proof".

This script is intentionally small glue around existing CANDELA components:
- uses src/guardian_runtime.py for enforcement + logging
- uses run_guardian.py bundle-hash logic to show provenance status (recorded in docs/ANCHORS.md or not)
- optionally anchors output batches via src/anchor_outputs.py (only if creds exist and user opts in)

It does NOT require any vendor system-prompt access. It demonstrates post-output governance and
tamper-evident receipts (optional) in a way that is quick for busy/sceptical reviewers.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]


def _resolve_ruleset_arg(arg: str | None) -> Path:
    """
    Resolve a reviewer-friendly ruleset selector.

    Default is the canonical baseline: src/directives_schema.json
    Optional packs live in ./rulesets/.
    """
    if not arg or arg.strip().lower() in ("baseline", "default"):
        return (ROOT / "src" / "directives_schema.json").resolve()

    a = arg.strip()
    low = a.lower()
    if low in ("security", "security_hardening"):
        return (ROOT / "rulesets" / "security_hardening.json").resolve()
    if low in ("privacy", "privacy_strict"):
        return (ROOT / "rulesets" / "privacy_strict.json").resolve()
    if low in ("health", "health_privacy", "health_privacy_micro"):
        return (ROOT / "rulesets" / "health_privacy_micro.json").resolve()

    p = Path(a).expanduser()
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    return p


def _read_text_from_file(p: Path) -> str:
    # Reuse the same extraction logic as run_guardian.py, but avoid importing it (it has import-time CWD side effects).
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        try:
            import pdfplumber

            with pdfplumber.open(str(p)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
        except ImportError:
            pass
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(p))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        except ImportError:
            print("ERROR: PDF support requires pdfplumber or pypdf.")
            print("  python3 -m pip install pdfplumber   (recommended)")
            print("  python3 -m pip install pypdf")
            raise SystemExit(1)

    return p.read_text(encoding="utf-8")


def _prompt(msg: str) -> str:
    try:
        return input(msg)
    except EOFError:
        return ""


def _print_header() -> None:
    print()
    print("CANDELA Demo (Reviewer UX)")
    print("- Goal: show post-output governance + audit logging quickly.")
    print("- Optional: show tamper-evident receipts via Merkle-root output anchoring.")
    print()


def _host_resolves(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False


def _configure_hf_offline(offline: bool) -> None:
    # Keep the reviewer demo crisp when DNS/network is unavailable.
    if offline:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


def _import_runtime(ruleset_path: Path):
    # Important: guardian_runtime reads CANDELA_RULESET_PATH at import time.
    os.environ["CANDELA_RULESET_PATH"] = str(ruleset_path)
    os.chdir(str(ROOT))
    sys.path.insert(0, str(ROOT))
    _configure_hf_offline(offline=not _host_resolves("huggingface.co"))
    import src.guardian_runtime as rt  # noqa: E402

    return rt


def _set_mode(rt, mode: str) -> None:
    rt.MODE = mode
    if mode == "regex_only":
        rt.SEM_ENABLED = False
    else:
        rt.SEM_ENABLED = bool(rt.CFG.get("detectors", {}).get("mini_semantic", {}).get("enabled", True))


def _run_modes(rt, text: str, modes: List[str]) -> List[Dict]:
    verdicts: List[Dict] = []
    for mode in modes:
        _set_mode(rt, mode)
        # Clear cache so timings reflect execution, not reuse.
        try:
            rt._cache.clear()  # type: ignore[attr-defined]
        except Exception:
            pass
        t0 = time.perf_counter()
        try:
            res = rt.guardian_chat(text)
            dt_ms = (time.perf_counter() - t0) * 1_000
            out = dict(res)
        except Exception as e:
            # Most common: semantic model cannot be fetched and is not cached.
            # Fall back to regex_only so reviewers still see the core value proposition.
            msg = str(e).strip() or e.__class__.__name__
            dt_ms = (time.perf_counter() - t0) * 1_000
            out = {"passed": False, "violations": [], "notes": [f"runtime_error:{msg}"], "score": 0}

            if mode != "regex_only":
                out["notes"].append("fallback:retrying_in_regex_only")
                _set_mode(rt, "regex_only")
                try:
                    rt._cache.clear()  # type: ignore[attr-defined]
                except Exception:
                    pass
                try:
                    res2 = rt.guardian_chat(text)
                    out = dict(res2)
                except Exception as e2:
                    out["notes"].append(f"regex_only_error:{str(e2).strip() or e2.__class__.__name__}")
        out["mode"] = mode
        out["wall_time_ms"] = round(dt_ms, 2)
        verdicts.append(out)
    return verdicts


def _print_verdicts(verdicts: List[Dict]) -> None:
    print()
    print("Verdict")
    any_fail = False
    for v in verdicts:
        status = "PASS" if v.get("passed") else "FAIL"
        viols = v.get("violations") or []
        print(f"- mode={v.get('mode')} result={status} wall={v.get('wall_time_ms')}ms violations={len(viols)}")
        if viols:
            any_fail = True
            print(f"  violations: {viols}")
        notes = v.get("notes") or []
        if notes:
            # Keep output short; detailed notes still live in logs/output_log.jsonl
            short = notes[:6]
            for n in short:
                print(f"  note: {n}")
            if len(notes) > len(short):
                print(f"  note: (+{len(notes)-len(short)} more)")
    if any_fail:
        print()
        print("NOTE: Full audit log entries are written to: logs/output_log.jsonl")


def _bundle_hash_status(ruleset_path: Path) -> Dict:
    # Import only the hashing helper (no network).
    import run_guardian as rg  # noqa: E402

    return rg.compute_bundle_hash(ruleset_path)


def _print_provenance(info: Dict) -> None:
    print()
    print("Ruleset Provenance")
    print(f"- ruleset: {info.get('ruleset_path')}")
    print(f"- directives: {info.get('directive_count')}")
    print(f"- SHA-256: {info.get('directive_bundle_hash')}")
    if info.get("hash_recorded_in_docs"):
        print("- status: recorded in docs/ANCHORS.md (verifiable)")
    else:
        print("- status: NOT recorded in docs/ANCHORS.md (provenance not published)")
        print("  (This is not necessarily malicious; it means this exact ruleset snapshot is not logged as anchored.)")


def _cold_start_time(ruleset_path: Path, mode: str, text: str) -> float:
    # True "cold start": new Python process.
    code = r"""
import os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(str(ROOT))
sys.path.insert(0, str(ROOT))
os.environ["CANDELA_RULESET_PATH"] = os.environ["CANDELA_RULESET_PATH"]
import src.guardian_runtime as rt
rt.MODE = os.environ.get("CANDELA_MODE", "strict")
rt.SEM_ENABLED = rt.MODE != "regex_only"
t0 = time.perf_counter()
rt.guardian_chat(os.environ["CANDELA_TEXT"])
dt = (time.perf_counter() - t0) * 1000
print(dt)
"""
    env = dict(os.environ)
    env["CANDELA_RULESET_PATH"] = str(ruleset_path)
    env["CANDELA_MODE"] = mode
    env["CANDELA_TEXT"] = text
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=str(ROOT), env=env)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "").strip())
    try:
        return float(proc.stdout.strip().splitlines()[-1])
    except Exception:
        raise RuntimeError(f"Unexpected cold-start output: {proc.stdout!r}")


def _maybe_anchor_outputs(allow_anchor: bool) -> None:
    if not allow_anchor:
        return
    rpc = os.getenv("SEPOLIA_RPC_URL")
    key = os.getenv("PRIVATE_KEY") or os.getenv("SEPOLIA_PRIVATE_KEY")
    if not rpc or not key:
        print()
        print("Anchoring skipped (missing SEPOLIA_RPC_URL and/or PRIVATE_KEY in .env).")
        return
    print()
    print("Anchoring output log batch on Sepolia (Merkle root)...")
    proc = subprocess.run([sys.executable, "src/anchor_outputs.py"], capture_output=True, text=True, cwd=str(ROOT))
    if proc.returncode != 0:
        print("ERROR: anchoring failed.")
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print(proc.stderr.strip())
        return
    if proc.stdout:
        print(proc.stdout.strip())


def _demo_once(
    *,
    ruleset_path: Path,
    text: str,
    modes: List[str],
    show_text_preview: bool,
    anchor_outputs: bool,
) -> None:
    rt = _import_runtime(ruleset_path)

    # Provenance summary first (reviewer trust).
    prov = _bundle_hash_status(ruleset_path)
    _print_provenance(prov)

    if show_text_preview:
        preview = text[:400]
        if len(text) > 400:
            preview += "\n\n[...truncated...]\n"
        print()
        print("Input Preview")
        print(preview)

    verdicts = _run_modes(rt, text, modes)
    _print_verdicts(verdicts)

    print()
    print("Evidence")
    print("- Local audit log: logs/output_log.jsonl")
    print("- Optional latency log: logs/latency_log.jsonl")
    print("- On-chain anchors list (if used): docs/ANCHORS.md")

    _maybe_anchor_outputs(anchor_outputs)


def main() -> int:
    ap = argparse.ArgumentParser(description="Reviewer-first CANDELA demo.")
    ap.add_argument(
        "--ruleset",
        default="baseline",
        help="baseline (default), security_hardening, privacy_strict, health_privacy_micro, or a path.",
    )
    ap.add_argument("--input", default="", help="Optional file to check (.txt/.md/.pdf).")
    ap.add_argument("--mode", choices=["strict", "sync_light", "regex_only"], default="strict")
    ap.add_argument("--all-modes", action="store_true", help="Run strict + sync_light + regex_only.")
    ap.add_argument("--anchor-outputs", action="store_true", help="Anchor output log batch (Merkle root) if creds exist.")
    ap.add_argument("--no-interactive", action="store_true", help="Run once and exit (no menus).")
    args = ap.parse_args()

    ruleset_path = _resolve_ruleset_arg(args.ruleset)
    if not ruleset_path.exists():
        print(f"ERROR: ruleset not found: {ruleset_path}")
        return 2

    modes = ["strict", "sync_light", "regex_only"] if args.all_modes else [args.mode]

    sample_text = (
        "Mary had a little lamb,\n"
        "its fleece was white as snow;\n"
        "and everywhere that Mary went,\n"
        "the lamb was sure to go.\n"
    )

    if args.no_interactive:
        text = sample_text
        if args.input:
            p = Path(args.input).expanduser().resolve()
            text = _read_text_from_file(p)
        _demo_once(
            ruleset_path=ruleset_path,
            text=text,
            modes=modes,
            show_text_preview=True,
            anchor_outputs=args.anchor_outputs,
        )
        return 0

    _print_header()
    print("Choose a ruleset to test (default is baseline).")
    print("  1) baseline (canonical)")
    print("  2) security_hardening (optional)")
    print("  3) privacy_strict (optional)")
    print("  4) health_privacy_micro (optional, micro-directives)")
    print("  5) keep current selection:", ruleset_path)
    sel = _prompt("Selection [1-5]: ").strip()
    if sel == "1":
        ruleset_path = _resolve_ruleset_arg("baseline")
    elif sel == "2":
        ruleset_path = _resolve_ruleset_arg("security_hardening")
    elif sel == "3":
        ruleset_path = _resolve_ruleset_arg("privacy_strict")
    elif sel == "4":
        ruleset_path = _resolve_ruleset_arg("health_privacy_micro")

    print()
    print("What do you want to check?")
    print("  1) Quick demo sample (recommended)")
    print("  2) Check a file (.txt/.md/.pdf)")
    print("  3) Paste text")
    print("  4) Cold vs hot start timing (strict mode)")
    print("  5) Exit")
    choice = _prompt("Choice [1-5]: ").strip()
    if choice == "5" or choice.lower() in ("q", "quit", "exit"):
        return 0

    if choice == "2":
        path_s = _prompt("Enter file path: ").strip()
        if not path_s:
            print("No path provided.")
            return 1
        p = Path(path_s).expanduser().resolve()
        if not p.exists():
            print(f"File not found: {p}")
            return 1
        text = _read_text_from_file(p)
    elif choice == "3":
        print("Paste text. End with a single line containing: EOF")
        lines: List[str] = []
        while True:
            ln = _prompt("")
            if ln.strip() == "EOF":
                break
            lines.append(ln)
        text = "\n".join(lines).strip()
        if not text:
            print("No text provided.")
            return 1
    elif choice == "4":
        # Timing-only flow.
        t = sample_text.strip()
        try:
            cold_ms = _cold_start_time(ruleset_path, "strict", t)
        except Exception as e:
            print(f"Cold-start test failed: {e}")
            return 1
        rt = _import_runtime(ruleset_path)
        _set_mode(rt, "strict")
        try:
            rt._cache.clear()  # type: ignore[attr-defined]
        except Exception:
            pass
        t0 = time.perf_counter()
        rt.guardian_chat(t)
        hot1 = (time.perf_counter() - t0) * 1_000
        try:
            rt._cache.clear()  # type: ignore[attr-defined]
        except Exception:
            pass
        t1 = time.perf_counter()
        rt.guardian_chat(t + " ")
        hot2 = (time.perf_counter() - t1) * 1_000

        print()
        print("Timing (approximate)")
        print(f"- cold start (new process): {cold_ms:.2f}ms")
        print(f"- hot start (same process, first run): {hot1:.2f}ms")
        print(f"- hot start (same process, second run): {hot2:.2f}ms")
        print()
        print("Cold start includes model import/load (if semantic is enabled). Hot start benefits from cached weights.")
        return 0
    else:
        text = sample_text

    print()
    print("Modes to run:")
    print("  1) strict (recommended)")
    print("  2) all modes (strict + sync_light + regex_only)")
    print("  3) regex_only (fastest)")
    msel = _prompt("Selection [1-3]: ").strip()
    if msel == "2":
        modes = ["strict", "sync_light", "regex_only"]
    elif msel == "3":
        modes = ["regex_only"]
    else:
        modes = ["strict"]

    anchor = _prompt("Anchor outputs (Merkle root) if creds exist? [y/N]: ").strip().lower() == "y"
    _demo_once(
        ruleset_path=ruleset_path,
        text=text,
        modes=modes,
        show_text_preview=True,
        anchor_outputs=anchor,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
