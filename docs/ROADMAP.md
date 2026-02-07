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

## Phase 0.2  — Performance Optimisation ✅ (Completed Aug 2025)  
| Item | Goal | Implementation steps |
|------|------|----------------------|
| **0.2-A Runtime cache + warm preload** | ≤10 ms fast-path latency | Branch `opt-cache` → add `src/guardian_runtime.py` → PR → tests → merge. |
| **0.2-B Latency budget keys** | Configurable ceiling | Add to `config/guardian_scoring.yaml`: `mode`, `latency_budget_ms`, `cache_ttl_s`. |
| **0.2-C SQLite persistent cache** *(optional)* | Verdict reuse after restart | Replace in-memory dict with `sqlite3` table. |
| **0.2-D Heavy-detector stub** | Off-path ML checks | Async hook in runtime file (currently NO-OP). |

Verification: `python3 -m pytest tests` + latency sample from `src/guardian_runtime.py`.

---

## Phase 0.3  — Semantic Guard & Release ✅ (Released v0.3 Feb 2026)  
| Task | Status | Notes |
|------|--------|-------|
| MiniLM semantic detector | Complete | `src/detectors/mini_semantic.py`, wired into runtime |
| Dependency update | Complete | `sentence-transformers`, `torch` added |
| Release & docs | Complete | v0.3 tag, Tech Spec v0.3, README/Getting Started |
| Anchoring | Complete | Directive bundle hash anchored on Sepolia (docs/ANCHORS.md) |

---

## Phase 0.4 — PoC Stabilisation (Active)  
Goal: finish a fully runnable PoC and lock the provenance trail.  
| Task | Status | Notes |
|------|--------|-------|
| Live Sepolia anchoring (SHA‑256) | Complete | Hash/tx recorded in `docs/ANCHORS.md` |
| Update `docs/ANCHORS.md` with tx | Complete | Auto‑append after anchoring |
| Run full local test + stress checks | Complete | pytest + runtime checks |
| Create reviewer run bundle | Complete | Review bundle + zip prepared |
| Output log + Merkle anchoring | Complete | JSONL log batched via `src/anchor_outputs.py` |

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

## Phase 1.2 — Service Layer & GUI (Future) ⚙️  
Goal: a web‑accessible interface for non‑developers to use Candela as a service.  
| Sub-task | Notes |
|---------|-------|
| Web GUI + accounts | Hosted portal for directive sets and audit views |
| Usage gating | Optional paid tiers or API keys |
| Run bundles | One‑click verification + exportable reports |

---

## Phase 1.3 — Tokenised Quality Incentives (post‑v1) ⚙️  
Goal: turn Guardian scoring into a verified, human‑quality signal and reward path.  
| Sub-task | Notes |
|---------|-------|
| Define quality thresholds | Publish score bands (e.g., 85/90/95) tied to directive compliance |
| Proof of human authorship | Build on Phase 1.1 (attestation + evidence bundle) |
| Human review layer | Community reviewers validate borderline/high‑impact content |
| Evidence bundle | Store: directive hash, score, violations, timestamp, signer, optional content hash |
| Issuance design | Start off‑chain credits; migrate to ERC‑20 only after abuse testing |
| Anti‑gaming controls | Reputation weights, sampling audits, rate limits, and reviewer cross‑checks |
| Anti‑abuse controls | Rate limits, reviewer sampling, appeal flow, audit logs |
| Pilot cohort | Small, vetted group to validate incentives and false‑positive rates |
| Public badge | “Candela‑Verified” stamp + link to evidence bundle |
| Governance safeguards | Transparent rules; revocation if evidence is invalid |

---

## Phase 2.0  — Detector Plug-In Stubs ⚙️  
Interface `src/detectors/base.py`; empty subclasses for stylometry, watermark, k-NN.

---

## Phase 3.0  — Example Gallery & Benchmarks ⚙️  
`examples/` pass/fail corpus; `scripts/benchmark.py` to print latency & scores.

---

## Additional concepts (post‑v1, optional)

### Ransomware Defence-in-Place 🛡️  
1. Hourly snapshot → Merkle root anchored.  
2. File-system filter driver hashes target pre-write.  
3. First violation ⇒ read-only freeze + alert + mount clean snapshot.  
4. Recovery script `scripts/recover_snapshot.sh` suggests restore.

### DAO Governance  
Multisig contract controlling directive hash anchor; community vote for rule updates.

---

## Cryptographic Provenance (reference)  
Anchored directive hash: `7b8d69ce…c73d`  
Sepolia tx: `0x2653a983ce75c31de39ab4b53c01fada024aac170c2fc99b7845f8df4702db70`  
Reproducibility test hash: `7b8d69ce…c73d`

---

## Current Position (as of now)  
- PoC codebase is runnable locally with tests passing.  
- Live anchoring is the final blocker before declaring PoC complete.  
- Once anchoring succeeds, Phase 0.4 completes and the project sits at the start of Phase 0.3 (external review).  

---

**Maintainer:** @jebus197 | **Last updated:** 17 Aug 2025  
