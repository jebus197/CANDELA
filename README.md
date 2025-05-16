# CANDELA: Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring

**Proof-of-Concept Repository (v0.1)**  
*Lead: George Jackson (jebus197), 2024-2025*

---

## What is CANDELA?

**CANDELA** (Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring) is a research-driven framework and middleware for verifiable, auditable, and reproducible alignment of large language models (LLMs) and autonomous agents.  
It anchors the directives (rules, constraints, policies) guiding an LLM’s behavior to public blockchains, ensuring that any LLM output can be traced, checked, and audited against a canonical set of directives.

This repository is a **working proof-of-concept (PoC, v0.1)** implementing the core ideas and demonstrating cryptographic anchoring, schema validation, and workflow integration.

---

## Quick Start

**Requirements:**
- Python 3.8+
- `requests` (see `requirements.txt`)
- (Optional for future: `web3.py` for blockchain anchoring)

**Run the main PoC script:**
```bash
cd src
python guardian_poc_v0.1.py
```

**Run the minimal smoke test:**
```bash
pip install pytest
pytest tests/
```

---

## Project Structure

```
CANDELA/
├── src/
│   ├── guardian_poc_v0.1.py        # Main PoC middleware script
│   ├── guardian_prototype.py       # Minimal working prototype
│   ├── guardian_extended.py        # Advanced PoC with LLM & blockchain hooks
│   ├── directives_schema.json      # Canonical directive set (v3.2, PoC)
│   └── requirements.txt            # Python dependencies for src/
├── tests/
│   └── test_directive_schema.py    # Smoke test for schema integrity
├── docs/
│   ├── README.md                   # Extended documentation
│   ├── Tech_Spec.md                # Technical specification
│   ├── ROADMAP.md                  # Milestones & future work
│   ├── FAQ.md                      # Frequently Asked Questions
│   ├── PROJECT_BRIEF.md            # Non-technical summary
│   ├── Licence                     # MIT License
│   ├── directives_README.md        # Directive schema documentation
│   └── example_directives_schema_annotated.jsonc  # Annotated schema example
├── CITATION.cff                    # Citation metadata
├── requirements.txt                # Top-level dependencies
├── .gitignore                      # Files to exclude from version control
└── README.md                       # This file
```

---

## Source Code Overview

- `src/guardian_poc_v0.1.py`: Main PoC; loads directives, validates LLM output, anchors hashes (mocked).
- `src/guardian_prototype.py`: Minimal working prototype of the workflow.
- `src/guardian_extended.py`: Adds error handling, token budget, LLM and blockchain hooks (commented).
- `src/directives_schema.json`: Canonical set of 76 directives (version 3.2, PoC).
- `tests/test_directive_schema.py`: Smoke test for presence and integrity of the directive schema.

---

## Documentation

- [docs/README.md](docs/README.md): Extended documentation, usage, and rationale.
- [docs/Tech_Spec.md](docs/Tech_Spec.md): Technical specification and architecture.
- [docs/ROADMAP.md](docs/ROADMAP.md): Roadmap and future milestones.
- [docs/FAQ.md](docs/FAQ.md): FAQ about approach, blockchain, and methodology.
- [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md): Non-technical summary and elevator pitch.
- [docs/directives_README.md](docs/directives_README.md): Format, rationale, and micro-directives schema.
- [docs/example_directives_schema_annotated.jsonc](docs/example_directives_schema_annotated.jsonc): Human-friendly, comment-annotated schema sample.

---

## License and Citation

- [docs/Licence](docs/Licence): MIT License, open use and adaptation.
- [CITATION.cff](CITATION.cff): Please cite this repository if used in academic or policy work.

---

## Versioning and Integrity

- **Directive schema (v3.2, PoC)**:  
  SHA-256: `3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa`
- This hash is checked by the test suite and referenced in all code and documentation.

---

## Questions, Issues, Contributions

- See [docs/FAQ.md](docs/FAQ.md) for philosophy and technical rationale.
- Open issues or pull requests for questions, suggestions, or contributions.
- Contact: George Jackson (jebus197) via GitHub.

---

## Acknowledgements

CANDELA is developed independently as a research and policy demonstration tool.  
Special thanks to the open source and AI alignment communities.

---
