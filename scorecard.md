# Candela Readiness Scorecard (v0.3)

Current score (self-assessed): **7.5 / 10** (Research Beta v0.3; strict-by-default, async opt-in)

Strengths
- Directive hash anchored on-chain; output provenance via log → Merkle root → on-chain anchor.
- Semantic guard integrated (MiniLM / all-MiniLM-L6-v2), modes configurable (strict default), warm preload, latency logging.
- Tooling: verify_output (Merkle proof generation), latency_stats, reviewer bundle.
- Docs aligned (README, Tech_Spec, Project_Brief, Roadmap, Anchors).

Gaps to reach 9/10
1) Proof UX: API/CLI to fetch anchored root, produce Merkle proof, and verify against chain (end-to-end demo).
2) Performance evidence: publish p50/p95 latency on common CPU (cold/warm, strict/sync_light), add to README/Tech_Spec.
3) Service hardening: auth/rate limits, health/metrics, CI (tests+lint), basic monitoring/alerts.
4) Prompt-injection & safety extensions: implement planned detectors/policies; document coverage.
5) Human-in-loop QA (Anti-Slop): minimal reviewer queue + credit ledger; tie into output anchoring flow.
6) Real model caller: replace mock path in guardian_prototype/Tech_Spec with working API integration for demo.

Next actions
- Add proof endpoint/CLI that validates a log line against the latest anchored root on-chain.
- Run latency benchmarks, record p50/p95 in docs and scorecard.
- Stand up basic CI (pytest) and health/metrics endpoints.

Updated: 2026-02-06
