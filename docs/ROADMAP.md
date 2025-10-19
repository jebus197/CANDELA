# CANDELA • Roadmap & Implementation Guide  
*(living document — update after each milestone)*  

Legend  
✅ completed 🟡 active 🔒 design-only ⚙️ future  

---

## Phase 0.1  — Proof-of-Concept ✅ (Completed May 2025)  
| Deliverable | How it was implemented |
|-------------|------------------------|
| Core Guardian (regex + directive scoring) | `src/guardian_extended.py` |
| Directive set v3.2 (76 rules) | `src/directives_schema.json` + Sepolia anchor (`docs/ANCHORS.md`) |
| Reproducibility tests | `tests/test_regex_guard.py`, `test_directive_schema.py` |
| Public DOI + OSF landing | OSF project `10.17605/OSF.IO/3S7BT`, README badge |
| **Setup hint** | Recommended: `python -m venv venv && source venv/bin/activate` |

---

## Phase 0.2  — Performance Optimisation 🟡 (Active Aug 2025)  
| Item | Goal | Implementation steps |
|------|------|----------------------|
| **0.2-A Runtime cache + warm preload** | ≤10 ms fast-path latency | Branch `opt-cache` → add `src/guardian_runtime.py` → PR → tests → merge. |
| **0.2-B Latency budget keys** | Configurable ceiling | Add to `config/guardian_scoring.yaml`: `mode`, `latency_budget_ms`, `cache_ttl_s`. |
| **0.2-C SQLite persistent cache** *(optional)* | Verdict reuse after restart | Replace in-memory dict with `sqlite3` table. |
| **0.2-D Heavy-detector stub** | Off-path ML checks | Async hook in runtime file (currently NO-OP). |

Verification: `python3 -m pytest tests` + `scripts/latency_check.py`.

---

## Phase 0.3  — Outreach & External Review ⚙️ (Planned Q4 2025)  
| Task | How we’ll do it |
|------|-----------------|
| One-pager PDF | `docs/CANDELA_one_pager.md` → PDF → upload to OSF |
| Expert contacts | Dr Bryson, Foresight Foundation, GovAI, compliance vendors |
| Target list | `outreach/targets.csv` (name, org, email, focus) |
| Feedback capture | `outreach/feedback.md` + GitHub issues |

Success: ≥3 detailed expert reviews; roadmap recalibrated.

---

## Phase 1.0  — Prompt-Injection Defence Extension 🔒  
| Sub-task | Implementation |
|----------|----------------|
| 1.0-A Directive additions | Add reserved-token & Unicode blacklist rows to `directives_schema.json`. |
| 1.0-B Context assembler | `src/prompt_builder.py` constructs `[SYSTEM|GUARDIAN|USER]`. |
| 1.0-C Instant lock | In runtime wrapper: raise `GuardianLockError`, set volume read-only. |
| 1.0-D Hash-ledger | `scripts/hash_prompt.py` → Merkle root → anchor weekly. |
| 1.0-E Heavy ML detector | Install via `pip install promptarmor`; integrate in async hook. |

---

## Phase 1.1  — Origin-Verification Design Note 🔒  
*File:* `docs/Origin_Verification.md` — spec for human-authorship proof.

---

## Phase 2.0  — Detector Plug-In Stubs ⚙️  
Interface `src/detectors/base.py`; empty subclasses for stylometry, watermark, k-NN.

---

## Phase 3.0  — Example Gallery & Benchmarks ⚙️  
`examples/` pass/fail corpus; `scripts/benchmark.py` to print latency & scores.

---

## Stretch Concepts (optional, unscheduled)

### Anti-Slop Quality Incentives  
Use Guardian score to mint CQT (ERC-20). Requires Phase 1.1 proof path.

### Ransomware Defence-in-Place 🛡️  
1. Hourly snapshot → Merkle root anchored.  
2. File-system filter driver hashes target pre-write.  
3. First violation ⇒ read-only freeze + alert + mount clean snapshot.  
4. Recovery script `scripts/recover_snapshot.sh` suggests restore.

### DAO Governance  
Multisig contract controlling directive hash anchor; community vote for rule updates.

---

## Cryptographic Provenance (reference)  
Anchored directive hash: `c2664a99e…e9cd`  
Sepolia tx: `0x0ca63893…9d56c` *(view on Etherscan)*  
Reproducibility test hash: `7b8d69ce…c73d`

---

**Maintainer:** @jebus197 | **Last updated:** 17 Aug 2025  
