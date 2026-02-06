# CANDELA Visuals (lightweight)

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
    A[Input] --> B{Regex pass?}
    B -->|No| X[Block: regex rule]
    B -->|Yes| C{Mode}
    C -->|strict| D[Semantic check]
    C -->|sync_light| E[Return response; semantic async]
    C -->|regex_only| F[Skip semantic]
    D -->|Fail| X
    D -->|Pass| G[Log + Merkle batch + anchor]
    E --> G
    F --> G
```

These diagrams avoid extra dependencies (rendered by GitHub Mermaid). For a static illustration of “allowed vs blocked” intents, prefer an offline PNG/SVG generated during docs build to keep runtime deps lean.
