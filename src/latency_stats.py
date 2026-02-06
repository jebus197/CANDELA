#!/usr/bin/env python3
"""
latency_stats.py
Compute simple latency stats from logs/latency_log.jsonl.

Usage:
  python3 src/latency_stats.py

Outputs p50/p95 for fast path and semantic path (where present), broken down by mode.
"""
import json, statistics
from pathlib import Path

LOG = Path("logs/latency_log.jsonl")

if not LOG.exists():
    raise SystemExit("logs/latency_log.jsonl not found; run guardian first.")

rows = []
for line in LOG.read_text().splitlines():
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError:
        pass

if not rows:
    raise SystemExit("No latency entries found.")

def pct(vals, p):
    if not vals:
        return None
    vals = sorted(vals)
    k = (len(vals)-1) * p
    f = int(k)
    c = min(f+1, len(vals)-1)
    if f == c:
        return vals[f]
    return vals[f] + (vals[c]-vals[f]) * (k-f)

by_mode = {}
for r in rows:
    m = r.get("mode", "unknown")
    by_mode.setdefault(m, {"fast": [], "sem": []})
    by_mode[m]["fast"].append(r.get("dt_fast_ms", 0))
    if r.get("dt_sem_ms") is not None:
        by_mode[m]["sem"].append(r["dt_sem_ms"])

for mode, vals in by_mode.items():
    f50 = pct(vals["fast"], 0.5)
    f95 = pct(vals["fast"], 0.95)
    s50 = pct(vals["sem"], 0.5) if vals["sem"] else None
    s95 = pct(vals["sem"], 0.95) if vals["sem"] else None
    print(f"Mode: {mode}")
    print(f"  fast p50: {f50:.3f} ms, p95: {f95:.3f} ms")
    if s50 is not None:
        print(f"  sem  p50: {s50:.3f} ms, p95: {s95:.3f} ms")
    else:
        print("  sem: n/a")

print("Entries analysed:", len(rows))
