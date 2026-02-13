# CANDELA Test Suite Results

**Generated:** 2026-02-11 18:06:34 UTC
**Profile:** quick
**Duration:** 10s
**System:** Darwin arm64, 8.0GB RAM, Python 3.9.6
**Framework Version:** v0.3 PoC (Enterprise Ruleset E1.0)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 20 |
| Passed | 20 |
| Failed | 0 |
| Verdict | **ALL PASS** |

## Phase 2: Unit Tests

| Test | Status | Time |
|------|--------|------|
| expanded_directives | PASS | 0.2ms |
| expanded_merkle | PASS | 0.2ms |
| existing_repo_tests | PASS | 0.2ms |

## Phase 3: Mode Integration

| Test | Status | Time |
|------|--------|------|
| clean_regex_only | PASS | 0.1ms |
| clean_sync_light | PASS | 1.5s |
| clean_strict | PASS | 3.7s |
| violation_regex_only | PASS | 0.1ms |
| violation_sync_light | PASS | 1.5s |
| violation_strict | PASS | 1.5s |

## Phase 4: Ruleset Validation

| Test | Status | Time |
|------|--------|------|
| baseline_clean | PASS | 0.1ms |
| baseline_violation | PASS | 0.1ms |
| security_hardening_clean | PASS | 0.1ms |
| security_hardening_violation | PASS | 0.1ms |
| privacy_strict_clean | PASS | 0.1ms |
| privacy_strict_violation | PASS | 0.1ms |
| health_privacy_micro_clean | PASS | 0.1ms |
| health_privacy_micro_violation | PASS | 0.1ms |
| custom_custom_canary | PASS | 0.1ms |
| custom_custom_clean | PASS | 0.1ms |
| custom_custom_long | PASS | 0.1ms |

Bundle hash verified in ANCHORS.md: YES

## Performance Profile

CANDELA's own validation is consistently sub-30ms for inputs up to 100KB.
Model generation latency depends on model choice, hardware, and precision.

**Measured (this system):**
- System: Darwin arm64, 8.0GB RAM

**Projected (optimised server, 32-core/64GB):**
- 1KB input: ~0.5-1ms
- 100KB input: ~6-14ms
- Rapid-fire: ~0.05-0.1ms

*These projections are estimates based on linear scaling characteristics.
Subject to revision by third-party benchmarks.*
