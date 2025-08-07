# CANDELA

CANDELA: Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring

[![DOI](https://img.shields.io/badge/DOI-10.17605%2FOSF.IO%2F3S7BT-blue.svg)](https://doi.org/10.17605/OSF.IO/3S7BT)
➡️ [Quick-Start Guide](GETTING_Started.md)

Illuminating AI: An Introduction to CANDELA

Large Language Models (LLMs) are rapidly transforming our digital landscape, offering remarkable capabilities in generating text, understanding queries, and even creating code. 
Their power is undeniable. Yet, alongside this power come significant challenges: LLMs can be unpredictable, producing incorrect or nonsensical information ("hallucinations"), 
subtly deviating from initial instructions over time ("drift"), and often operating as "black boxes" whose internal decision-making processes remain opaque. This inherent lack 
of consistent reliability, true transparency, and verifiable governance is a critical barrier to deploying AI confidently in high-stakes scenarios and fostering widespread 
public trust.

CANDELA (Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring) is an open-source project designed to address these fundamental issues head-on.

At its heart, CANDELA introduces an external software framework called the "Directive Guardian." This system acts as a verifiable control layer that works with any LLM, rather 
than attempting to alter the LLM's core architecture. The Guardian's role is to ensure that the LLM adheres to a clearly defined, human-readable, and machine-parsable set of 
behavioral and cognitive rules known as the "Directive Scaffold." The core innovation of CANDELA lies in its approach to ensuring the integrity and consistent application of 
these rules:

    Verifiable Rule-Set Integrity: Before any LLM interaction, the entire Directive Scaffold (stored as src/directives_schema.json) is given a unique cryptographic fingerprint 
    (a 
    
    SHA-256 hash). This hash is then "anchored" onto a public blockchain (initially a testnet for our Proof-of-Concept). This crucial step makes the governing rule-set 
    transparent, tamper-proof, and its exact version publicly verifiable by anyone, at any time.
    Runtime Verification & Guided Output: The Guardian software loads its local copy of the directives, calculates its hash, and verifies it against the canonical hash retrieved 
    from the blockchain. Only upon confirming this integrity does it use the validated directives to strategically construct prompts and guide the LLM's output.
    Automated Compliance Checks: Following LLM generation, the Guardian is designed to perform automated checks to assess whether the output complies with specific "micro-
    directives"—granular, testable components derived from more complex conceptual rules within the scaffold.
    Transparent Audit Trails: The CANDELA framework facilitates the creation of a clear, auditable link from the enforced rules, through the LLM's input, to its final output, 
    with the potential to also anchor interaction-specific hashes on-chain for comprehensive accountability. By externalizing governance and making the rules of engagement 
    explicit, verifiable, and consistently applied, CANDELA aims to significantly improve the reliability, transparency, and trustworthiness of AI systems. This project is 
    currently at a Proof-of-Concept stage (v0.1), having successfully demonstrated the core hashing mechanism of the directive set and its symbolic manual anchoring. We believe 
    this "pre-execution rule anchoring" and validation approach offers a practical and impactful step towards developing 
    AI that operates more predictably, ethically, and responsibly.


Key features of CANDELA include:

- **Human-Readable Directive Scaffold:** Define and manage model behaviors with clear, interpretable directives that are easy to understand and audit.
- **Blockchain Anchoring:** Secure each directive and behavioral change with blockchain technology, ensuring transparency and preventing unauthorized modifications.
- **Verifiable Governance:** Enable collaborative and decentralized oversight, making LLM decision processes open to scrutiny and improvement.
- **Python Implementation:** Built with Python, CANDELA is accessible, extensible, and readily integrable into modern AI workflows.

By bridging the gap between human oversight and machine intelligence, CANDELA sets a new standard for responsible AI development. Whether you are an AI researcher, developer, or 
an organization seeking robust governance over LLM behaviors, CANDELA provides the tools necessary to establish trust, transparency, and accountability in your AI deployments.

---

## 🛡️ From Rule-Checker to **Anti-Slop Quality-Token Engine**

### The new digital pollution

Large-language models can now spin out billions of words per day at near-zero cost.  
That tsunami of low-effort, machine-generated text—call it **AI slop**—already clogs search results, poisons future model training, and crowds out human craft. Existing spam filters catch the worst abuses, but nothing yet **rewards** the opposite: painstaking, human-authored content that obeys rigorous reasoning, ethics, and transparency standards.

### Why CANDELA is the missing piece

CANDELA’s core insight is that every output can be **provably measured** against an immutable rule-set:

* **Directive bundle** anchored on Ethereum Sepolia (SHA-256 `c2664a99…e9cd`, tx `0x0ca63893…d56c`).  
* **Guardian** middleware that enforces those 70+ directives in real time.  
* **Test suite + hash log** so any researcher can reproduce verdicts offline.

That infrastructure is already live for pass/fail gating. The natural extension is to **flip the incentive**: pay creators for passing with flying colours, and penalise attempts to sneak in AI slop.

### How the Quality-Token layer works

1. **AI-Contamination Filter** - An ensemble of open-source detectors (stylometry burstiness, watermark scan, k-NN distance to LLM corpora). Any positive hit ⇒ hard fail.  
2. **Guardian Quality Score** - Each directive category now carries a weight (see `config/guardian_scoring.yaml`). Score = 100 − Σ(weight × violations).  
3. **Mint “Candela Quality Token” (CQT)** - If contamination = False *and* score ≥ 80, the Guardian verifier wallet mints `(score − 80)` tokens (capped 20) to the author.  
4. **Stake & Slash** - Submitter locks 1 CQT per artefact. On failure the stake is burned, deterring mass spam. Subsequent audits can burn tokens retroactively if hidden slop surfaces.  
5. **On-chain provenance** - The artefact’s SHA-256, Guardian report, and minted amount are logged in `docs/ANCHORS.md` and referenced by the mint transaction.

Result: high-effort human work accrues tangible value; AI slop becomes economically self-defeating.

### Implementation roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **P-0** | Scoring YAML + Guardian numeric output | ✅ committed |
| **P-1** | AI-contamination plug-in interface (4 detectors) | ⚙ in progress |
| **P-2** | `CandelaQualityToken.sol` (ERC-20 mint/burn) on Sepolia | scaffold committed |
| **P-3** | `candela-claim` CLI — local verify → on-chain mint | scaffold committed |
| **P-4** | Pilot cohort (10 essays) & public leaderboard | planned |
| **P-5** | DAO / multisig for rule & treasury governance | planned |

### Why this isn’t “just another badge”

* **Cryptographic proof** — Anyone can run `sha256sum file`, replay Guardian, and match the on-chain record.  
* **Adaptive filter** — Detectors are plug-ins; new AI watermarks or stylometry tricks drop straight into layer 1.  
* **Positive-sum** — Writers earn tokens tied to demonstrable quality, not eyeball-time or clickbait.

**Clone, test, and reproduce** every proof:  
```bash
git clone https://github.com/jebus197/CANDELA && cd CANDELA
python3 -m pytest tests


→ New here? Read **[GETTING_STARTED.md](GETTING_STARTED.md)** for a 10-minute walkthrough.


---

## Project Overview

CANDELA is a project developing a novel framework to enhance Large Language Model (LLM) reliability and transparency using a human-readable directive scaffold and blockchain anchoring for verifiable behaviour governance.

## Features

- **Directive Scaffold:** Establish and enforce clear, human-readable rules for LLM behavior.
- **Blockchain Anchoring:** All behavioral updates and directives are recorded on a blockchain, ensuring auditability and tamper-resistance.
- **Transparency:** Every change is visible and verifiable, supporting open governance and trust.
- **Python-Based:** 100% Python implementation for easy integration and extensibility.
- Anti-AI-Slop Features. Roadmaps takes us to a condition where the same technology can be flipped to ensure high quality human-only-centric content, incorportating a token reward system for content that meets the defined on-chain directive anchorred standard.

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/jebus197/CANDELA.git
   cd CANDELA
   ```

2. **Set Up Your Environment:**
   - Ensure you have Python 3.8+ installed.
   - (Optional) Create and activate a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Configuration:**
   - Update any configuration files as needed for your environment or blockchain anchoring requirements.

4. **Run CANDELA:**
   - Refer to the [documentation](./docs/README.md) for details on running the main modules and interacting with the directive scaffold.

## Documentation

- Please see the [docs folder](./docs/) for detailed documentation, API references, and usage guides.

## Contributing

We welcome contributions from the community! To get started, please read our [contributing guidelines](./CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

For questions, issues, or suggestions, please open an [issue](https://github.com/jebus197/CANDELA/issues) or contact the maintainer directly via GitHub.

---

*Empowering transparent, reliable, and accountable AI through human-guided governance and blockchain technology.*
