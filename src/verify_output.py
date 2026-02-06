#!/usr/bin/env python3
"""
verify_output.py
Generate a Merkle proof for a specific output log entry and print the root.

Usage:
  python3 src/verify_output.py --line 42
  python3 src/verify_output.py --hash <text_sha256>

- Reads logs/output_log.jsonl (append-only log produced by guardian_runtime).
- Uses the same Merkle construction as anchor_outputs.py (sha256 of each JSONL line; pairwise up the tree).
- Prints: selected entry, its proof, and the computed Merkle root.
Compare the root to the latest anchored root in docs/ANCHORS.md / Etherscan.
"""
import argparse, hashlib, json
from pathlib import Path
from typing import List, Tuple

LOG_FILE = Path("logs/output_log.jsonl")


def leaf_hash(line: str) -> bytes:
    return hashlib.sha256(line.encode("utf-8")).digest()


def merkle_root_and_proof(leaves: List[bytes], index: int) -> Tuple[bytes, List[bytes]]:
    if not leaves:
        raise ValueError("No leaves")
    proof: List[bytes] = []
    level = leaves
    idx = index
    while len(level) > 1:
        if idx % 2 == 0:
            pair_idx = idx + 1 if idx + 1 < len(level) else idx
            sibling = level[pair_idx]
        else:
            sibling = level[idx - 1]
        proof.append(sibling)
        # build next level
        nxt = []
        it = iter(range(0, len(level), 2))
        for i in it:
            a = level[i]
            b = level[i + 1] if i + 1 < len(level) else a
            nxt.append(hashlib.sha256(a + b).digest())
        idx //= 2
        level = nxt
    return level[0], proof


def find_index_by_hash(lines: List[str], text_sha: str) -> int:
    for i, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("text_sha256") == text_sha:
            return i
    raise ValueError("No entry with that text_sha256")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--line", type=int, help="1-based line number in output_log.jsonl")
    ap.add_argument("--hash", dest="text_sha", help="text_sha256 to locate entry")
    args = ap.parse_args()

    if not LOG_FILE.exists():
        raise SystemExit("logs/output_log.jsonl not found; run guardian_runtime first.")

    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise SystemExit("output_log.jsonl is empty.")

    if args.text_sha:
        idx = find_index_by_hash(lines, args.text_sha)
    elif args.line:
        idx = args.line - 1
        if idx < 0 or idx >= len(lines):
            raise SystemExit("Line number out of range.")
    else:
        raise SystemExit("Provide --line N or --hash <text_sha256>")

    leaves = [leaf_hash(l) for l in lines]
    root, proof = merkle_root_and_proof(leaves, idx)

    entry = json.loads(lines[idx])
    print("Entry #{}:".format(idx + 1))
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    print("\nMerkle root:", root.hex())
    print("Proof (hex, order = sibling up the tree):")
    for h in proof:
        print(h.hex())
    print("\nCompare this root to the anchored root in docs/ANCHORS.md / Etherscan.")


if __name__ == "__main__":
    main()
