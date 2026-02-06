# CANDELA – Developer Notes

> TL;DR  
> • Tag before risky edits • Branch for experiments • Push tags.

---

## Naming conventions
| Kind   | Pattern               | Example              |
|--------|-----------------------|----------------------|
| Tag    | `v{major}.{minor}`    | `v0.2`               |
| Backup | `backup/{tag}`        | `backup/poc_v0.1`    |
| Feature| `feat/{short-desc}`   | `feat/api-wrapper`   |

---

## One-liner recipes

### Snapshot current state (local only)
```bash
git checkout main
git tag -a v0.2-draft -m "Stable before validator refactor"
git branch backup/v0.2-draft
# push only when you explicitly decide to publish
