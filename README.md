### CANDELA

Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring

[![DOI](https://img.shields.io/badge/DOI-10.17605%2FOSF.IO%2F3S7BT-blue.svg)](https://doi.org/10.17605/OSF.IO/3S7BT) · [Quick-Start Guide](GETTING_Started.md)

## Illuminating AI: An Introduction to CANDELA

Large Language Models (LLMs) are transforming the way we write, code, and search. Their power is undeniable—and so are the challenges: hallucinations, instruction drift, and opaque internals.

CANDELA addresses this with an external software layer—the **Directive Guardian**—that enforces a clear, human-readable, machine-parsable **Directive Scaffold**.

### How CANDELA keeps rules consistent and verifiable

- **Verifiable rule-set integrity.** Before any LLM interaction, the directive scaffold (stored as `src/directives_schema.json`) is hashed (SHA-256). The digest is **anchored** on a public blockchain (testnet for PoC), making the rule-set transparent, tamper-evident, and publicly verifiable.
- **Runtime verification & guided output.** The Guardian loads its local copy, recomputes the hash, and verifies it against the on-chain value. Only if they match does it proceed to guide the LLM’s output.
- **Automated checks (selective).** After generation, the Guardian can evaluate outputs against **microdirectives**—small, testable rules derived from the scaffold—used **only where they add clarity**.
- **Transparent audit trails.** Optionally anchor interaction-specific hashes for provenance when needed.

### Key features

- **Human-readable directives.** Define and manage model **behaviour** with clear, interpretable rules that are easy to audit.  
- **Blockchain anchoring.** Secure directive updates with public anchoring for transparency and tamper resistance.  
- **Verifiable governance.** Enable collaborative, decentralised oversight of model behaviour.  
- **Python implementation.** Accessible, extensible, and easy to integrate.

By bridging the gap between human oversight and machine intelligence, CANDELA aims to raise the standard for responsible AI development. Whether you are an AI researcher, developer, or an organisation seeking robust governance over LLM behaviours, CANDELA provides tools to establish trust, transparency, and accountability.

---

## From Rule-Checker to **Anti-Slop Quality-Token Engine**

**The new digital pollution.** LLMs can produce vast quantities of low-effort text (**AI slop**) that clog search, poison future training data, and crowd out human craft. Spam filters catch some abuse; few systems **reward** the opposite: careful, human-authored work that meets rigorous standards.

**Why CANDELA is the missing piece.** Built for **platforms**, **publishers**, and **researchers** who need auditable, tamper-evident rules for LLM behaviour. CANDELA’s insight: outputs can be **provably measured** against an immutable rule-set.

> **Proof you can check now**
>
> 1) View the canonical hash and transaction in [`docs/ANCHORS.md`](docs/ANCHORS.md).  
> 2) Recompute locally:
>
> ```bash
> sha256sum src/directives_schema.json
> # macOS:
> shasum -a 256 src/directives_schema.json
> ```
>
> Compare to the value in `docs/ANCHORS.md` (and the linked on-chain record).

That infrastructure enables pass/fail gating. The next step is incentives: reward high-quality human work; make slop economically self-defeating.

### Implementation roadmap (high level)

- **P-0** — Guardian numeric output + scoring weights — ✅  
- **P-1** — AI-contamination plug-in interface — ⚙ in progress  
- **P-2** — Token scaffolding (mint/burn) on Sepolia — ⚙ in progress  
- **P-3** — `candela-claim` CLI (local verify → record) — ⚙ in progress  
- **P-4** — Pilot cohort + public leaderboard — planned  
- **P-5** — DAO / multisig governance — planned

### Clone, test, reproduce

~~~bash
git clone https://github.com/jebus197/CANDELA && cd CANDELA
python3 -m pytest tests
~~~

New here? Read **[GETTING_Started.md](GETTING_Started.md)** for a 10-minute walkthrough.

---

## Project Overview

CANDELA develops a framework to enhance LLM reliability and transparency via a human-readable directive scaffold and blockchain anchoring for verifiable **behavioural** governance.

### Features

- **Directive Scaffold:** establish and enforce clear, human-readable rules for LLM **behaviour**.  
- **Blockchain Anchoring:** record behavioural updates and directives on a blockchain for auditability and tamper-resistance.  
- **Transparency:** every change is visible and verifiable, supporting open governance and trust.  
- **Python-Based:** 100% Python implementation for easy integration and extensibility.

## Getting Started

1. **Clone the repository**

~~~bash
git clone https://github.com/jebus197/CANDELA.git
cd CANDELA
~~~

2. **Set up your environment**

- Python 3.8+  
- (Optional) virtual environment:

~~~bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
~~~

- Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

3. **Run CANDELA**

- See the [`docs/`](docs/) folder and the Quick-Start for details.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licence

MIT — see [`LICENSE`](LICENSE).
