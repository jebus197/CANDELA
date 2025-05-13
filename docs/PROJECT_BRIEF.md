# CANDELA – Project Brief (v0.1)

## Elevator Pitch

CANDELA adds a blockchain-anchored **Guardian layer** in front of any LLM.  
It turns fragile prompt rules into verifiable, auditable governance.

How CANDELA helps defend against “AI-slop” and the “dead-internet” problem

| AI-slop symptom                                                                              | Why it happens                                                                                                                    | CANDELA counter-mechanism                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Flood of low-effort, copy-pasted content**<br>(no provenance, no incentives for originals) | Anyone can paste scraped text into an LLM and publish instantly; nothing ties outputs back to a stable rule-set or source ledger. | • **Immutable directive bundle** requires every generation to disclose a provenance hash.<br>• Planned **content-signature extension**: Guardian appends the SHA-256 of both the directive set *and* the model response → readers (or search engines) can filter for “signed-by-CANDELA” material only.<br>• Future v0.4 roadmap item: optional “original-source URL array” micro-directive that forces citation lines machine-checkable. |
| **Bots citing hallucinated facts / no audit trail** 
| LLMs compress context, drop sources, invent publishers.                                                                           
| • Directive 3 (truthfulness & non-deception) + 10 (explicit uncertainty) + micro-directives (“Conf: 0-1”, “Source:”) give a *machine-verifiable* footprint.<br>• Guardian validator rejects any answer missing at least one source line → impossible to publish through a CANDELA-wrapped API without citations.                                                                                                                          |
| **Search results full of SEO bait**                                                          
| Ranking algorithms can’t distinguish handcrafted vs. auto-generated.                                                              
| • Because every CANDELA response carries a public hash anchored on-chain, search engines could whitelist “hash-backed” pages, penalising anonymous slop.  (Proposal already logged in ROADMAP.md v0.4 “Search-engine plug-in”.)                                                                                                                                                                                                           |
| **No incentives for human creators**                                                         | Traffic & ad revenue drop when summaries replace clicks.                                                                          | • CANDELA ledger can include **revenue-split metadata**: hash ⟶ original-author wallet.<br>• That makes it trivial for platforms to tip original writers automatically, restoring an economic loop.                                                                                                                                                                                                                                       |
| **Users can’t detect bot vs human**                                                          | Content signatures aren’t standardised.                                                                                           | • A lightweight browser plug-in could query the CANDELA blockchain and turn the hash green (verified) or red (unsigned).  PoC planned for v0.5.                                                                                                                                                                                                                                                                                           |

Why directives matter

    Without the rule-set, Guardian would happily pass through any text and merely stamp a hash.

    Directives force the model to expose premise / source / confidence so that low-effort slop fails the validator.

Concrete next deliverables (slots into ROADMAP)

| Milestone | Added feature                                           | Directives needed                    |
| --------- | ------------------------------------------------------- | ------------------------------------ |
| **v0.2**  | “Must-include source” micro-directive & validator regex | Extend IDs 30-32                     |
| **v0.3**  | Content-hash footer in every API response               | New ID 78 “Append HashFooter = true” |
| **v0.4**  | Search-engine demo filtering for on-chain hashes        | No new directives; integration work  |
| **v0.5**  | Browser plug-in colour-codes CANDELA-signed pages       | n/a                                  |


Why we don’t embed exhaustive decompositions now

    Keeping first-principles & associative-reasoning at the 6-step level is enough to demonstrate machine-checkable depth.

    Further “concept-link” decompositions will live in the v0.3 schema once we wire the validation-tier engine. That avoids bloating the POC while giving reviewers a clear path forward.



## Problem & Vision
LLMs can be steered by instructions, but those instructions are volatile and invisible to third parties.  
CANDELA delivers an immutable directive bundle, rapid auto-validation, and a public hash so anyone can prove which rules were active.

## Current Status (May 2025)
- **Directive bundle**: 76 rules + 2 showcase micro-directive blocks  
- **Prototype**: loads JSON, hashes bundle, displays hash  
- **Docs**: README, tech spec, directive rationale, roadmap

## Key Components
1. **Guardian Prototype** – Python middleware (src/)  
2. **Directive Schema** – strict JSON, machine-checkable  
3. **Validation Tiers** – auto / semi / human (coming v0.2)  
4. **Hash Anchoring** – Ethereum Sepolia test-net (planned v0.3)

## Roadmap Snapshot
| Milestone | Target |
|-----------|--------|
| Validation-tier engine | Jun 2025 |
| Test-net anchoring demo | Jul 2025 |
| Public beta & case study | Q4 2025 |

## Quick Start
```bash
git clone https://github.com/your-org/CANDELA.git
cd CANDELA
pip install -r requirements.txt
python3 src/guardian_prototype.py
Contributing

See the issues tab. We welcome PRs on:

    Validation regexes / heuristic checks

    Blockchain anchoring strategies

    Additional micro-directive templates

---

### Next minimal steps

1. Create `docs/PROJECT_BRIEF.md` with the template.  
2. Link it in `README.md`.  
3. Commit & push:

```bash
git add docs/PROJECT_BRIEF.md README.md
git commit -m "Add concise Project Brief for onboarding"
git push origin main
