# CANDELA

**Compliant Auditable Natural-language Directive Enforcement & Ledger Anchoring**

* **Quick-Start Guide:** [GETTING_Started.md](GETTING_Started.md)
* **OSF DOI:** [10.17605/OSF.IO/3S7BT](https://doi.org/10.17605/OSF.IO/3S7BT)

---

### The Problem: The Unpredictability of Modern AI

Large Language Models (LLMs) are powerful tools, but they come with inherent risks for any organisation where trust, safety, and compliance are paramount. Unpredictable outputs ("hallucinations"), gradual deviation from instructions ("drift"), and opaque "black box" reasoning make it difficult to deploy them in mission-critical roles.

### The Solution: A Verifiable Governance Framework

**CANDELA is a model-agnostic—and more importantly, intelligence-agnostic—governance framework.** It acts as an external "Guardian" that applies the same rigorous standards of verification to all output, whether the author is human or machine.

This Guardian enforces a clear, human-readable set of rules (a "Directive Scaffold") and uses blockchain anchoring to create a permanent, tamper-evident audit trail for those rules. The result is a fast, reliable, and transparent system for ensuring AI tools operate safely and predictably, without needing to alter their complex internal architecture.



> **The Core Idea:** By separating the rules (the *what*) from the model (the *how*), Candela makes AI governance explicit, auditable, and reliable.

---

### Project Journey & Roadmap

This project is evolving through distinct phases, moving from a robust foundation to a wider ecosystem.

#### ✅ **Phase 0: The Foundation (Complete)**

The initial goal was to prove the core concept: that an external governance layer could verifiably enforce a set of rules. This phase delivered:
* A **Core Guardian** capable of regex and semantic checks (Mini‑BERT detector in `src/detectors/mini_semantic.py`).
* The first **On-Chain Anchoring** of the directive set on the Sepolia testnet, creating a permanent, cryptographic proof of the rules.
* A full **Reproducibility Suite** (`pytest`) to ensure the integrity of the framework can be independently verified.

#### 🟡 **Phase 1: Hardening & Outreach (Active)**

The current focus is on making the PoC robust, efficient, and ready for expert review. This involves:
* **Performance Optimisation:** Implementing a low-latency runtime with caching to ensure the Guardian is fast enough for real-time use without impacting user experience.
* **Community Outreach:** Engaging with experts in AI safety, security, and compliance to gather feedback and stress-test the framework's principles.
* **Documentation Polish:** Creating a "single source of truth" through clear documentation (like this README) and a professional landing page on the Open Science Framework (OSF).

#### ⚙️ **Phase 2: Building the Ecosystem (Future)**

The next stage is to expand Candela from a standalone PoC into an extensible platform. This will involve:
* **Standardised Plug-in Interfaces:** Creating a formal API for third-party "detectors" (e.g., for prompt injection, stylometry, or other specialised checks) to integrate with the Guardian.
* **A Benchmark Gallery:** Developing a public repository of pass/fail examples to provide a clear benchmark for the Guardian's performance and to help the community contribute new tests.

---

### Long-Term Vision: A Framework for Digital Trust

CANDELA is designed as a foundational technology for verifiable governance. Its core principles can be extended far beyond simple AI output checking. The concepts below are speculative, long-term examples of the framework's power.

* **Prompt Injection Defence:** The Guardian's rule-set can be extended to detect and block malicious prompt-injection attacks at both the input and output stages, with the entire "session recipe" anchored on-chain for forensic analysis.

* **Ransomware Defence:** The framework could be adapted to govern file-system operations, using on-chain anchored file-state hashes (Merkle roots) to detect and block the unauthorised mass-encryption characteristic of ransomware.

* **Incentivising Quality (Post-v1.0): The "Anti-Slop" Engine**
    Down the roadmap, after the core governance framework is mature, its principles could be used to address the growing problem of low-quality, machine-generated "AI slop." The Guardian's scoring mechanism could power a "Quality Token Engine," creating a tangible economic incentive that **rewards human creators** for producing verifiably high-quality, directive-compliant work. This remains a conceptual exploration focused on using verifiable quality to foster a healthier digital ecosystem.

---

### Getting Started

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/jebus197/CANDELA.git](https://github.com/jebus197/CANDELA.git) && cd CANDELA
    ```
2.  **Set Up Your Environment**
    * Python 3.8+ is required.
    * (Optional but recommended) Create and activate a virtual environment.
    * Install dependencies (includes `sentence-transformers` and `torch`, which are larger downloads): `pip install -r requirements.txt`
3.  **Run Tests to Verify Integrity**
    ```bash
    python3 -m pytest tests
    ```

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

### Licence
MIT — see [LICENSE](LICENSE).
