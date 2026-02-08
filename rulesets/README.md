# Optional Demo Rulesets

By default, CANDELA uses the baseline demo ruleset:
- `src/directives_schema.json`

Reviewers can optionally select an additional demo ruleset:
- `rulesets/security_hardening.json`
- `rulesets/privacy_strict.json`

These packs exist to demonstrate extensibility without making the first run a multiple-choice setup step.

For on-chain provenance, you can anchor any selected pack with:
`python3 src/anchor_hash.py --path rulesets/<pack>.json`

