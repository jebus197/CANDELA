# Anchors (Sepolia)

This file is the human-readable index of on-chain anchors used by CANDELA.

It is split into:
- Ruleset anchors (hash of `src/directives_schema.json`)
- Output batch anchors (Merkle roots over `logs/output_log.jsonl` lines)

## Ruleset anchors

- `bddd2587745d1d86a4d14cf006025386a218e4550642ca236ca6b682125e3f6a` → [366897af7bf3c53c2d3025ca0fdf1c99562d3529f7cb2241528ab4c2531dd753](https://sepolia.etherscan.io/tx/366897af7bf3c53c2d3025ca0fdf1c99562d3529f7cb2241528ab4c2531dd753)
- `c2664a99eb7f98f46d368815184158cbd74b8572d61974663c45726f8235e9cd` → [0ca63893d44bc2fe6fd28202b7cbfcdfa7ed6727739e195b43f3e17d29e9d56c](https://sepolia.etherscan.io/tx/0ca63893d44bc2fe6fd28202b7cbfcdfa7ed6727739e195b43f3e17d29e9d56c)
- `164c9e03ecc7b77d2e0a831cc5e0105d425878f60ef2751f4775dd241c1da267` → [efc87e7dad6acdfc50696728ae22683348bfe83661f713af717cfbdad47b1ecc](https://sepolia.etherscan.io/tx/efc87e7dad6acdfc50696728ae22683348bfe83661f713af717cfbdad47b1ecc)  # superseded (raw-bytes hash; use canonical JSON hash below)
- `7b8d69ce1ca0a4c03e764b7c8f4f2dc64416dfc6a0081876ce5ff9f53a90c73d` → [2653a983ce75c31de39ab4b53c01fada024aac170c2fc99b7845f8df4702db70](https://sepolia.etherscan.io/tx/2653a983ce75c31de39ab4b53c01fada024aac170c2fc99b7845f8df4702db70)

## Output batch anchors

- Each run of `src/anchor_outputs.py` anchors a Merkle root of new `logs/output_log.jsonl` lines.
- The log entry includes line ranges so a specific output can be proven by showing the log line plus its Merkle proof against the anchored root.

