FAQ

# CANDELA – Frequently Asked Questions

---

### 1. What problem does CANDELA solve?
LLM behaviour can drift over time, and post-hoc logs alone cannot verify what rules were in force when a response was generated.  
CANDELA anchors a machine-readable directive bundle on a public blockchain **before** generation, validates each reply against concrete micro-directives, and then hashes the input/output pair to the same chain. The entire reasoning path is therefore transparent and tamper-evident.

---

### 2. Why micro-directives?
Large, abstract rules like “apply first-principles reasoning” are interpreted inconsistently across different models.  
CANDELA breaks such concepts into **micro-directives** (e.g., 6a-c, 24a-c) that form short checklists. This makes behaviour reproducible, easy to validate with pattern matching, and model-agnostic.

---

### 3. How does CANDELA differ from FICO Auditable AI or Prove AI?
Those platforms hash trained models and runtime logs **after** execution.  
CANDELA hashes the **behavioural rule-set before execution**. Combining the two approaches yields complete provenance: intent → execution → audit.

---

### 4. Why use a blockchain?
A blockchain hash provides an immutable, time-stamped record of the rule-set and each I/O bundle. Anyone can recompute the hash to confirm that the same directives and outputs were used—no need to trust a private server or database.

---

### 5. Do I need blockchain expertise to use CANDELA?
No. The prototype ships with mock anchoring. Switching to Polygon testnet (or another chain) is a two-line change in `src/guardian_extended.py` using `web3.py`. Detailed instructions are in **TECH_SPEC.md**.

---

### 6. How do I extend the validation logic?
* Add or edit entries in `directives_schema.json`, specifying `validation_criteria` for each micro-directive.  
* Update the `validate_response()` function in `guardian_extended.py` to include regex checks or call lightweight NLP models.  
* Write unit tests in the `tests/` folder to assert compliance automatically.

---

### 7. Is CANDELA open source?
Yes. All code and directive schemas are MIT-licensed. Contributions are welcome via Pull Requests.

---

### 8. Roadmap
| Version | Milestone |
|---------|-----------|
| **v0.1** | Proof of Concept (hash rule-set, mock anchor, minimal validator) |
| **v0.2** | Real LLM integration + testnet anchoring |
| **v0.3** | Comprehensive validator suite + CI unit tests |
| **v1.0** | Optional integration with existing audit-trail platforms (FICO, Prove AI) |

---

### 9. Who maintains CANDELA?
The project is led by the original researcher who independently conceived directive anchoring, with community contributions via GitHub. Future governance will migrate to a small DAO once adoption grows.

---

### 10. How can I get involved?
1. ⭐ Star the repo to follow updates.  
2. File issues for bugs or directive suggestions.  
3. Submit Pull Requests for code, tests, or documentation.  
4. Join the upcoming Discord (link in README) for discussions.

---

*CANDELA – illuminating AI governance through verifiable directives.*
```
