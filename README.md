*CANDELA*

Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring
DOI: 10.17605/OSF.IO/3S7BT (https://doi.org/10.17605/OSF.IO/3S7BT)
Quick-Start Guide: GETTING_Started.md

Illuminating AI: An Introduction to CANDELA

Large Language Models (LLMs) are transforming the way we write, code, and search. Their power is undeniable—and so are the challenges: hallucinations, instruction drift, and opaque internals.

CANDELA addresses this with an external software layer (the Directive Guardian) that enforces a clear, human-readable, machine-parsable Directive Scaffold.

How CANDELA keeps rules consistent and verifiable:

- Verifiable rule-set integrity: before any LLM interaction, the entire Directive Scaffold (stored as src/directives_schema.json) is hashed (SHA-256). The digest is anchored on a public blockchain (testnet for PoC), making the rule-set transparent, tamper-evident, and publicly verifiable.
- Runtime verification and guided output: the Guardian loads its local copy, recomputes the hash, and verifies it against the on-chain value. Only if they match does it proceed to guide the LLM’s output.
- Automated compliance checks: after generation, the Guardian evaluates outputs against microdirectives—granular, testable rules derived from the scaffold (used selectively where they add clarity).
- Transparent audit trails: the framework supports anchoring interaction-specific hashes for full provenance when needed.

Key features of CANDELA

- Human-readable Directive Scaffold: define and manage model behaviour with clear, interpretable directives that are easy to audit.
- Blockchain anchoring: secure each directive and behavioural change with blockchain technology, ensuring transparency and preventing unauthorised modifications.
- Verifiable governance: enable collaborative and decentralised oversight, making LLM decision processes open to scrutiny and improvement.
- Python implementation: built with Python; accessible, extensible, and readily integrable into modern AI workflows.

By bridging the gap between human oversight and machine intelligence, CANDELA aims to raise the standard for responsible AI development. Whether you are an AI researcher, developer, or an organisation seeking robust governance over LLM behaviours, CANDELA provides tools to establish trust, transparency, and accountability.

From Rule-Checker to Anti-Slop Quality-Token Engine

The new digital pollution:
LLMs can produce vast quantities of low-effort text (AI slop) that clog search, poison future training data, and crowd out human craft. Spam filters catch some abuse; few systems reward the opposite: careful, human-authored work that meets rigorous standards.

Why CANDELA is a missing piece:
Built for platforms, publishers, and researchers who need auditable, tamper-evident rules for LLM behaviour. CANDELA’s insight: outputs can be assessed against an immutable rule-set in a verifiable way.

Proof you can check now
1) View the canonical hash and transaction in docs/ANCHORS.md.
2) Recompute locally:
   $ sha256sum src/directives_schema.json
   (macOS) $ shasum -a 256 src/directives_schema.json
   Compare to the value in docs/ANCHORS.md and the linked on-chain record.

That infrastructure enables simple pass/fail gating. The next step is incentives: reward high-quality human work; make slop economically self-defeating.

Implementation roadmap (high level)
- P-0: Guardian numeric output + scoring weights — DONE
- P-1: AI-contamination plug-in interface — IN PROGRESS
- P-2: Token scaffolding (mint/burn) on Sepolia — IN PROGRESS
- P-3: candela-claim CLI (local verify -> record) — IN PROGRESS
- P-4: Pilot cohort + public leaderboard — PLANNED
- P-5: DAO / multisig governance — PLANNED

Clone, test, reproduce
$ git clone https://github.com/jebus197/CANDELA && cd CANDELA
$ python3 -m pytest tests

New here? Read GETTING_Started.md for a 10-minute walkthrough.

Project Overview
CANDELA develops a framework to enhance LLM reliability and transparency via a human-readable directive scaffold and blockchain anchoring for verifiable behavioural governance.

Features
- Directive Scaffold: establish and enforce clear, human-readable rules for LLM behaviour.
- Blockchain Anchoring: all behavioural updates and directives are recorded on a blockchain, ensuring auditability and tamper-resistance.
- Transparency: every change is visible and verifiable, supporting open governance and trust.
- Python-Based: 100% Python implementation for easy integration and extensibility.

Getting Started
1) Clone the repository
   $ git clone https://github.com/jebus197/CANDELA.git
   $ cd CANDELA
2) Set up your environment
   - Python 3.8+
   - (Optional) virtual environment:
     $ python -m venv venv
     $ source venv/bin/activate   (Windows: venv\Scripts\activate)
   - Install dependencies:
     $ pip install -r requirements.txt
3) Run CANDELA
   See the docs/ folder and the Quick-Start for details.

Contributing
See CONTRIBUTING.md

Licence
MIT — see LICENSE

Tagline
Empowering transparent, reliable, accountable AI through human-guided governance and ledger anchoring.
