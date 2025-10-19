# CANDELA
**Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

[![DOI](https://img.shields.io/badge/DOI-10.17605%2FOSF.IO%2F3S7BT-blue.svg)](https://doi.org/10.17605/OSF.IO/3S7BT)  
Quick-Start Guide: [GETTING_Started.md](GETTING_Started.md)

---

### A Functional Framework for AI Governance
Large Language Models are powerful yet unpredictable—hallucinations, instruction drift, opaque reasoning.  
**CANDELA** is a fully functional famework that adds a thin, model-agnostic “Guardian” that checks every output against a publicly anchored rule-set and records a tamper-evident audit trail. No changes to model internals, minimal latency.

---

## Status & Direction (SSOT)

| Item | Value |
|------|-------|
| **Mode** | `sync_light` — fast path (regex + directive scoring) |
| **Rewards** | Disabled; all token ideas strictly future/optional |
| **Anchored directive hash** | `c2664a99eb7f98f46d368815184158cbd74b8572d61974663c45726f8235e9cd` |
| **Sepolia tx** | 0x0ca63893d44bc2fe6fd28202b7cbfcdfa7ed6727739e195b43f3e17d29e9d56c |
| **Reproducibility test hash** | `7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d` |
| **Long-term vision PDF** | docs/Candela_Extended.pdf |

---

## Low-Latency Architecture
Governance adds **<10 ms**:

1. **Guardian fast path** — regex safety + directive scoring (synchronous).  
2. **Optional heavy detectors** — watermark / perplexity / k-NN run **only** off-path or in future “claim” flow.  
3. **Content-hash cache** (planned) — repeat messages skip all checks.

Result: Guardian behaves like a simple gateway, not a multi-agent bottleneck.

---

## Core Features

* Human-readable directives — easy to audit and update.  
* Blockchain anchoring — SHA-256 root hash stored on Sepolia; rules are publicly verifiable.  
* Reproducible audits — all anchor events live in docs/ANCHORS.md.

---

## Future Applications (optional, not in POC)
* Anti-slop quality incentives — reward human creators for high-score content (design only).  
* Ransomware defence-in-place — file-system Guardian to block mass encryption (concept only).

---

## Roadmap (governance-first)

- R-0 Governance hardening & reproducibility — active  
- R-1 OSF polish & outreach — active  
- R-2 Origin-verification design note — groundwork  
- R-3 Detector plug-in stubs — future  
- R-4 Example gallery & benchmarks — future  
- R-5 Independent review & hand-off — future

---

## Getting Started

```
git clone https://github.com/jebus197/CANDELA.git
cd CANDELA
python3 -m pytest tests
```

---

## Repository Layout

* src/guardian_extended.py — core Guardian (regex + directive scoring)  
* src/guardian_runtime.py — optional cache/warm-preload wrapper  
* src/directives_schema.json — anchored rule-set (do not edit casually)  
* config/guardian_scoring.yaml — weights, thresholds, latency labels  
* docs/ANCHORS.md — on-chain anchor log  
* docs/Candela_Extended.pdf — long-term vision  
* tests/ — reproducibility tests

---

## Contributing
See CONTRIBUTING.md. Work on dev, open PRs into main after tests pass; keep changes non-destructive.

## Licence
MIT — see LICENSE

Tagline  
Transparent, reliable, accountable AI through directive-anchored governance — fast today, extensible tomorrow.
