# CANDELA Visuals (lightweight)

Palette (RGB):
- Blue (outputs): `rgb(0,102,204)`
- Green (pass to Guardian): `rgb(0,153,0)`
- Red (stop/block): `rgb(204,0,0)`

## Guardian flow (sequence)
```mermaid
sequenceDiagram
    autonumber
    participant U as User/App
    participant G as Guardian
    participant R as Regex Check
    participant S as Semantic Check
    participant L as Output Log
    participant M as Merkle Batch
    participant C as Chain (Sepolia)

    U->>G: text
    G->>R: regex screen
    R-->>G: pass/fail
    alt regex fail
        G-->>U: block (regex)
    else regex pass
        G->>S: semantic (Mini-BERT)
        S-->>G: pass/fail
        alt strict mode
            G-->>U: block if fail
        else sync_light
            G-->>U: return (regex-cleared)
            Note over G,S: semantic runs async
        end
        G->>L: append log (hash, verdict)
        L->>M: batch into Merkle root (periodic)
        M->>C: anchor root on-chain
    end
```

## Mode selection (flow)
```mermaid
flowchart LR
    classDef blue fill:#0066cc,stroke:#004c99,color:white;
    classDef green fill:#009900,stroke:#006600,color:white;
    classDef red fill:#cc0000,stroke:#990000,color:white;

    A[Input]:::blue --> B{Regex pass?}:::blue
    B -->|No| X[Block: regex rule]:::red
    B -->|Yes| C{Mode}:::blue
    C -->|strict| D[Semantic check]:::blue
    C -->|sync_light| E[Return fast;<br/>semantic async]:::blue
    C -->|regex_only| F[Skip semantic]:::blue
    D -->|Fail| X
    D -->|Pass| G[Log + Merkle batch + anchor]:::green
    E --> G
    F --> G
```
Descriptions:
- Guardian flow shows input through regex and semantic checks, with strict vs sync_light branching, then logging, Merkle batching, and anchoring.
- Mode selection highlights outcomes with color cues: blue (processing/output path), green (pass/anchor), red (block).
