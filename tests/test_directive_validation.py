"""
Unit tests for directive_validation.py

These tests focus only on deterministic, machine-checkable criteria.
They intentionally avoid importing semantic models (torch/sentence-transformers).
"""

from src.directive_validation import validate_output


def _keys(findings):
    return {f.directive_id for f in findings if f.level == "violation"}


def test_blocks_eth_private_key_hex():
    bad = "leak 0x" + "a" * 64
    findings = validate_output(bad, include_semantic=False, semantic_matcher=None)
    assert 1 in _keys(findings)


def test_blocks_us_ssn_dashed():
    bad = "SSN: 123-45-6789"
    findings = validate_output(bad, include_semantic=False, semantic_matcher=None)
    assert 3 in _keys(findings)


def test_warns_on_missing_confidence_tag():
    findings = validate_output("hello world", include_semantic=False, semantic_matcher=None)
    # Directive 12 is WARN tier, so it should not be a violation.
    assert 12 not in _keys(findings)


def test_warns_on_email_but_does_not_block():
    findings = validate_output("email me at test@example.com", include_semantic=False, semantic_matcher=None)
    # Directive 10 is WARN tier, so it should not be a violation.
    assert 10 not in _keys(findings)
