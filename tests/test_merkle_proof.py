import hashlib

from src.verify_output import leaf_hash, merkle_root_and_proof


def _verify_proof(leaf: bytes, proof: list[bytes], index: int) -> bytes:
    """
    Recompute the Merkle root from a leaf + proof using the same left/right rule
    as src/verify_output.py: at each level, pair order depends on index parity.
    """
    h = leaf
    idx = index
    for sibling in proof:
        if idx % 2 == 0:
            h = hashlib.sha256(h + sibling).digest()
        else:
            h = hashlib.sha256(sibling + h).digest()
        idx //= 2
    return h


def test_merkle_proof_round_trip():
    lines = [
        '{"a":1}',
        '{"b":2}',
        '{"c":3}',
        '{"d":4}',
        '{"e":5}',
    ]
    leaves = [leaf_hash(l) for l in lines]
    index = 2

    root, proof = merkle_root_and_proof(leaves, index)
    recomputed = _verify_proof(leaves[index], proof, index)

    assert root == recomputed

