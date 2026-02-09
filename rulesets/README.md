# Optional Demo Rulesets

By default, CANDELA uses the baseline demo ruleset:
- `src/directives_schema.json`

Reviewers can optionally select an additional demo ruleset:
- `rulesets/security_hardening.json`
- `rulesets/privacy_strict.json`
- `rulesets/health_privacy_micro.json` (micro-directives demo; public sector / health privacy style)

These packs exist to demonstrate extensibility without making the first run a multiple-choice setup step.

For on-chain provenance, you can anchor any selected pack with:
`python3 src/anchor_hash.py --path rulesets/<pack>.json`

## Micro-directives (why this pack exists)
Some governance goals are "macro" statements (high-level intent) that are hard to test directly.

The micro-directives approach decomposes a macro goal into small, checkable rules, for example:
- Macro: "Do not disclose personal health data."
- Micro: "Block NI numbers", "Block emails", "Block UK phone numbers", "Block Luhn-positive card numbers", "Block semantic intent to reveal records".

This mirrors established practice in policy-as-code and compliance engineering:
control objectives become testable requirements that can be executed by tooling.
