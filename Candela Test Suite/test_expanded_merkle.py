#!/usr/bin/env python3
"""
Expanded Merkle Proof Tests — CANDELA Test Suite

Tests Merkle root computation and proof verification at various sizes.
Edge cases: single entry, power-of-2, non-power-of-2, large (100 entries).

Run from sandbox root:
  python3 -m pytest "Candela Test Suite/test_expanded_merkle.py" -v
"""
import hashlib
import json
import sys
from pathlib import Path

SANDBOX = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SANDBOX))


def leaf_hash(data: str) -> bytes:
    return hashlib.sha256(data.encode("utf-8")).digest()


def merkle_root_and_proof(leaves: list, index: int):
    """Compute Merkle root and proof for the leaf at `index`."""
    if not leaves:
        return None, []

    level = list(leaves)
    proof = []
    idx = index

    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            next_level.append(hashlib.sha256(left + right).digest())

            if i == idx or i + 1 == idx:
                sibling = right if i == idx else left
                direction = "right" if i == idx else "left"
                proof.append((direction, sibling))

        idx = idx // 2
        level = next_level

    return level[0], proof


def verify_proof(leaf: bytes, proof: list, index: int) -> bytes:
    """Recompute root from leaf and proof."""
    current = leaf
    for direction, sibling in proof:
        if direction == "right":
            current = hashlib.sha256(current + sibling).digest()
        else:
            current = hashlib.sha256(sibling + current).digest()
    return current


def simple_merkle_root(leaves: list) -> bytes:
    """Independent Merkle root computation (no proof)."""
    if not leaves:
        return None
    level = list(leaves)
    while len(level) > 1:
        it = iter(level)
        nxt = []
        for a in it:
            b = next(it, a)
            nxt.append(hashlib.sha256(a + b).digest())
        level = nxt
    return level[0]


# ─────────────────────────────────────────────
# Edge cases
# ─────────────────────────────────────────────

class TestMerkleEdgeCases:
    def test_single_entry(self):
        leaves = [leaf_hash('{"a":1}')]
        root = simple_merkle_root(leaves)
        assert root is not None
        # Single leaf: loop condition `len(level) > 1` is false, so root = leaf itself
        assert root == leaves[0], "Single leaf root should be the leaf hash itself"

    def test_two_entries(self):
        leaves = [leaf_hash('{"a":1}'), leaf_hash('{"b":2}')]
        root = simple_merkle_root(leaves)
        expected = hashlib.sha256(leaves[0] + leaves[1]).digest()
        assert root == expected

    def test_three_entries(self):
        leaves = [leaf_hash(f'{{"x":{i}}}') for i in range(3)]
        root = simple_merkle_root(leaves)
        assert root is not None
        assert len(root) == 32  # SHA-256


# ─────────────────────────────────────────────
# Power-of-2 sizes
# ─────────────────────────────────────────────

class TestMerklePowerOf2:
    def test_4_entries(self):
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(4)]
        root = simple_merkle_root(leaves)
        assert root is not None

    def test_8_entries(self):
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(8)]
        root = simple_merkle_root(leaves)
        assert root is not None

    def test_16_entries(self):
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(16)]
        root = simple_merkle_root(leaves)
        assert root is not None


# ─────────────────────────────────────────────
# Non-power-of-2 sizes
# ─────────────────────────────────────────────

class TestMerkleNonPowerOf2:
    def test_5_entries(self):
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(5)]
        root = simple_merkle_root(leaves)
        assert root is not None

    def test_10_entries(self):
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(10)]
        root = simple_merkle_root(leaves)
        assert root is not None

    def test_50_entries(self):
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(50)]
        root = simple_merkle_root(leaves)
        assert root is not None

    def test_100_entries(self):
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(100)]
        root = simple_merkle_root(leaves)
        assert root is not None


# ─────────────────────────────────────────────
# Proof verification at every leaf index
# ─────────────────────────────────────────────

class TestMerkleProofVerification:
    def test_proof_round_trip_5_entries(self):
        lines = [f'{{"entry":{i}}}' for i in range(5)]
        leaves = [leaf_hash(l) for l in lines]
        for idx in range(len(leaves)):
            root, proof = merkle_root_and_proof(leaves, idx)
            recomputed = verify_proof(leaves[idx], proof, idx)
            assert root == recomputed, f"Proof verification failed for index {idx}"

    def test_proof_round_trip_8_entries(self):
        lines = [f'{{"entry":{i}}}' for i in range(8)]
        leaves = [leaf_hash(l) for l in lines]
        for idx in range(len(leaves)):
            root, proof = merkle_root_and_proof(leaves, idx)
            recomputed = verify_proof(leaves[idx], proof, idx)
            assert root == recomputed, f"Proof verification failed for index {idx}"

    def test_proof_round_trip_13_entries(self):
        """Non-power-of-2, verify every leaf."""
        lines = [f'{{"entry":{i}}}' for i in range(13)]
        leaves = [leaf_hash(l) for l in lines]
        for idx in range(len(leaves)):
            root, proof = merkle_root_and_proof(leaves, idx)
            recomputed = verify_proof(leaves[idx], proof, idx)
            assert root == recomputed, f"Proof verification failed for index {idx}"


# ─────────────────────────────────────────────
# Consistency: independent root matches proof root
# ─────────────────────────────────────────────

class TestMerkleConsistency:
    def test_root_matches_between_methods(self):
        """Simple root computation and proof-based root should agree."""
        leaves = [leaf_hash(f'{{"n":{i}}}') for i in range(7)]
        simple_root = simple_merkle_root(leaves)
        proof_root, _ = merkle_root_and_proof(leaves, 0)
        assert simple_root == proof_root, "Root from simple computation should match proof root"

    def test_different_data_different_roots(self):
        leaves_a = [leaf_hash(f'{{"a":{i}}}') for i in range(5)]
        leaves_b = [leaf_hash(f'{{"b":{i}}}') for i in range(5)]
        root_a = simple_merkle_root(leaves_a)
        root_b = simple_merkle_root(leaves_b)
        assert root_a != root_b, "Different data should produce different roots"
