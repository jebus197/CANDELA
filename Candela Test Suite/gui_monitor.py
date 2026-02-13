#!/usr/bin/env python3
"""
GUI Monitor — watches the CANDELA GUI test suite and logs everything.

Tracks:
  - GUI process lifecycle (start, running, exit)
  - Child subprocesses (model loading, test runner, pip installs)
  - CPU/memory usage of GUI and children
  - Key file changes (results JSON, reports, model dirs)
  - Phase transitions (by watching results JSON)

Usage:
  python3.11 gui_monitor.py              # monitor already-running GUI
  python3.11 gui_monitor.py --launch     # launch GUI and monitor it

Output: timestamped log to stdout + gui_monitor.log
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "gui_monitor.log"
RESULTS_JSON = SCRIPT_DIR / "Candela Test Suite Results.json"
RESULTS_MD = SCRIPT_DIR / "Candela Test Suite Results.md"
MODELS_DIR = SCRIPT_DIR.parent / "models"


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(msg: str):
    line = f"[{ts()}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def find_gui_pid() -> int | None:
    """Find PID of running gui_test_suite.py."""
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", "gui_test_suite.py"], text=True
        ).strip()
        pids = [int(p) for p in out.split("\n") if p.strip()]
        # Filter out our own process
        pids = [p for p in pids if p != os.getpid()]
        return pids[0] if pids else None
    except (subprocess.CalledProcessError, ValueError):
        return None


def get_children(ppid: int) -> list[dict]:
    """Get child processes of a given PID."""
    try:
        out = subprocess.check_output(
            ["ps", "-o", "pid,ppid,rss,%cpu,command", "-ax"],
            text=True,
        )
        children = []
        for line in out.strip().split("\n")[1:]:
            parts = line.split(None, 4)
            if len(parts) >= 5:
                pid, parent, rss_kb, cpu, cmd = (
                    int(parts[0]), int(parts[1]),
                    int(parts[2]), parts[3], parts[4],
                )
                if parent == ppid:
                    children.append({
                        "pid": pid,
                        "rss_mb": round(rss_kb / 1024, 1),
                        "cpu": cpu,
                        "cmd": cmd[:120],
                    })
        return children
    except Exception:
        return []


def get_process_info(pid: int) -> dict | None:
    """Get memory/CPU for a specific PID."""
    try:
        out = subprocess.check_output(
            ["ps", "-o", "rss,%cpu", "-p", str(pid)],
            text=True,
        )
        lines = out.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            return {
                "rss_mb": round(int(parts[0]) / 1024, 1),
                "cpu": parts[1],
            }
    except Exception:
        return None


def check_results_json() -> dict | None:
    """Read the latest results JSON if it exists."""
    if RESULTS_JSON.exists():
        try:
            data = json.loads(RESULTS_JSON.read_text())
            phases = data.get("phases", [])
            summary = {}
            for p in phases:
                phase_num = p.get("phase", "?")
                passed = p.get("all_passed", p.get("passed", None))
                tests = p.get("tests", [])
                total = len(tests)
                ok = sum(1 for t in tests if t.get("passed"))
                summary[phase_num] = {
                    "passed": passed,
                    "tests": f"{ok}/{total}",
                }
            return summary
        except Exception:
            return None
    return None


def main():
    parser = argparse.ArgumentParser(description="Monitor CANDELA GUI")
    parser.add_argument("--launch", action="store_true",
                        help="Launch the GUI and monitor it")
    args = parser.parse_args()

    # Clear log
    LOG_FILE.write_text(f"=== GUI Monitor started {datetime.now().isoformat()} ===\n")

    gui_pid = None
    gui_proc = None

    if args.launch:
        log("Launching GUI...")
        gui_proc = subprocess.Popen(
            [sys.executable, str(SCRIPT_DIR / "gui_test_suite.py")],
            cwd=str(SCRIPT_DIR.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        gui_pid = gui_proc.pid
        log(f"GUI launched (PID {gui_pid})")
    else:
        gui_pid = find_gui_pid()
        if gui_pid:
            log(f"Found running GUI (PID {gui_pid})")
        else:
            log("No GUI running. Waiting for it to start...")

    # Track state changes
    last_children: set[int] = set()
    last_results_mtime = 0.0
    last_results_summary = None
    last_md_mtime = 0.0
    poll_count = 0

    try:
        while True:
            poll_count += 1
            time.sleep(1)

            # Find GUI if not yet found
            if not gui_pid:
                gui_pid = find_gui_pid()
                if gui_pid:
                    log(f"GUI started (PID {gui_pid})")
                continue

            # Check if GUI is still running
            try:
                os.kill(gui_pid, 0)
            except OSError:
                log(f"GUI process {gui_pid} has exited")
                if gui_proc:
                    stdout, stderr = gui_proc.communicate(timeout=2)
                    if stderr:
                        log(f"GUI stderr: {stderr.decode()[:500]}")
                break

            # Get GUI process info (every 5s)
            if poll_count % 5 == 0:
                info = get_process_info(gui_pid)
                if info:
                    log(f"GUI: {info['rss_mb']} MB RAM, {info['cpu']}% CPU")

            # Watch child processes
            children = get_children(gui_pid)
            child_pids = {c["pid"] for c in children}

            # New children
            new_pids = child_pids - last_children
            for c in children:
                if c["pid"] in new_pids:
                    # Identify what the child is doing
                    cmd = c["cmd"]
                    if "run_test_suite" in cmd:
                        log(f"  CHILD SPAWNED: Test runner (PID {c['pid']})")
                    elif "test_model_integration" in cmd:
                        log(f"  CHILD SPAWNED: Model integration test (PID {c['pid']}) — MODEL IS LOADING")
                    elif "pip install" in cmd:
                        pkg = cmd.split("install")[-1].strip()[:40]
                        log(f"  CHILD SPAWNED: pip install {pkg} (PID {c['pid']})")
                    elif "run_guardian" in cmd:
                        log(f"  CHILD SPAWNED: Guardian run (PID {c['pid']})")
                    elif "anchor_outputs" in cmd:
                        log(f"  CHILD SPAWNED: Anchor (PID {c['pid']})")
                    elif "demo_model_guardian" in cmd:
                        log(f"  CHILD SPAWNED: Interactive model session (PID {c['pid']})")
                    else:
                        log(f"  CHILD SPAWNED: PID {c['pid']} — {cmd[:80]}")

            # Exited children
            gone_pids = last_children - child_pids
            for pid in gone_pids:
                log(f"  CHILD EXITED: PID {pid}")

            # Report child memory (every 5s, only if children exist)
            if poll_count % 5 == 0 and children:
                for c in children:
                    if c["rss_mb"] > 10:  # only report significant memory users
                        log(f"  CHILD PID {c['pid']}: {c['rss_mb']} MB, {c['cpu']}% CPU — {c['cmd'][:60]}")

            last_children = child_pids

            # Watch results JSON
            if RESULTS_JSON.exists():
                mtime = RESULTS_JSON.stat().st_mtime
                if mtime > last_results_mtime:
                    last_results_mtime = mtime
                    summary = check_results_json()
                    if summary and summary != last_results_summary:
                        log(f"RESULTS UPDATED:")
                        for phase, info in sorted(summary.items()):
                            status = "PASS" if info["passed"] else "FAIL"
                            log(f"  Phase {phase}: {status} ({info['tests']} tests)")
                        last_results_summary = summary

            # Watch report MD
            if RESULTS_MD.exists():
                mtime = RESULTS_MD.stat().st_mtime
                if mtime > last_md_mtime:
                    last_md_mtime = mtime
                    size = RESULTS_MD.stat().st_size
                    log(f"REPORT WRITTEN: {RESULTS_MD.name} ({size} bytes)")

    except KeyboardInterrupt:
        log("Monitor stopped by user")

    log("Monitor finished")


if __name__ == "__main__":
    main()
