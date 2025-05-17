# CANDELA Documentation

**Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**  
*Proof-of-Concept Repository (v0.1)*  
Lead: George Jackson (jebus197), 2024-2025

---

## Overview

**CANDELA** provides a framework for verifiable, auditable, and reproducible alignment of large language models (LLMs) and autonomous agents. By anchoring directive schemas (rules, constraints, policies) to public blockchains and ensuring their cryptographic integrity, CANDELA enables robust auditing and accountability for AI outputs.

This documentation covers the design, usage, and rationale behind the CANDELA proof-of-concept.

---

## Key Resources

- [Project root README](../README.md) — Project summary, structure, and quick start.
- [Technical Specification](Tech_Spec.md) — Detailed architecture and workflow.
- [Roadmap](ROADMAP.md) — Milestones and planned features.
- [FAQ](FAQ.md) — Philosophy, blockchain usage, and methodology.
- [Project Brief](PROJECT_BRIEF.md) — Non-technical summary and elevator pitch.
- [Directive Schema Documentation](directives_README.md) — Format, rationale, and micro-directives schema.
- [Example Annotated Directive Schema](example_directives_schema_annotated.jsonc) — Human-friendly, comment-annotated JSONC sample.
- [MIT License](Licence)
- [Citation Metadata](../CITATION.cff)

---

## Source Code Overview

- [`src/guardian_poc_v0.1.py`](../src/guardian_poc_v0.1.py): Main PoC script; loads directives, validates LLM output, anchors hashes (mocked).
- [`src/guardian_prototype.py`](../src/guardian_prototype.py): Minimal working prototype illustrating core workflow.
- [`src/guardian_extended.py`](../src/guardian_extended.py): Adds error handling, token budget, LLM and blockchain hooks (commented).
- [`src/directives_schema.json`](../src/directives_schema.json): Canonical set of 76 directives (version 3.2, PoC).
- [`tests/test_directive_schema.py`](../tests/test_directive_schema.py): Smoke test for presence and integrity of the directive schema.

---

## Integrity and Reproducibility

The canonical directive schema (v3.2, PoC) is cryptographically anchored:

- **SHA-256:** `3cf5a9178cf726ed33ba0754fca66003ec469671a7cb799534052dccc6bddffa`

This hash is checked by the test suite and referenced throughout the codebase and documentation.  
To verify, use the included script in [`tests/test_directive_schema.py`](../tests/test_directive_schema.py).

→ First-time testers: see **[GETTING_STARTED.md](GETTING_STARTED.md)** for a 10-minute walkthrough.

---

## Contributing and Contact

- For technical questions, see the [FAQ](FAQ.md) or open a GitHub issue.
- Pull requests and contributions are welcome!
- Contact: George Jackson (jebus197) via GitHub.

---

## Acknowledgements

CANDELA is developed independently as a research and policy demonstration tool.  
Special thanks to the open source and AI alignment communities.

---
