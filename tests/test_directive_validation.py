"""
Unit tests for directive_validation.py

These tests focus only on deterministic, machine-checkable criteria.
They intentionally avoid importing semantic models (torch/sentence-transformers).
"""

from src.directive_validation import validate_output


def _keys(findings):
    return {f.key for f in findings if f.level == "violation"}


def test_confidence_advisory_by_default():
    findings = validate_output("hello world")
    # Should not hard-fail by default, but should note missing confidence
    assert "3/71" not in _keys(findings)


def test_confidence_format_violation_when_present():
    findings = validate_output("Confidence: Maybe\nhello")
    assert "71" in _keys(findings)


def test_logical_extension_requires_premise_and_inference_when_triggered():
    findings = validate_output("Premise: something")
    keys = _keys(findings)
    assert "6b" in keys  # missing Inference


def test_logical_extension_inference_word_and_period_checks():
    findings = validate_output("Premise: a\nInference: " + ("word " * 25))
    keys = _keys(findings)
    assert "6c" in keys

    findings2 = validate_output("Premise: a\nInference: short but no period")
    keys2 = _keys(findings2)
    assert "6c" in keys2


def test_associative_reasoning_checks_after_related():
    findings = validate_output("Related: cats")
    keys = _keys(findings)
    assert "14b" in keys
    assert "14c" in keys


def test_first_principles_is_marker_triggered_only():
    # Bullet list alone should not trigger 24b without the marker
    findings = validate_output("- fact one\n- fact two")
    assert "24b" not in _keys(findings)

    # Marker triggers enforcement
    findings2 = validate_output(
        "First-Principles\nthis is a restatement that is definitely too long for the strict fifteen word limit right now\n- fact one\n- fact two\n"
    )
    keys2 = _keys(findings2)
    assert "24a" in keys2
