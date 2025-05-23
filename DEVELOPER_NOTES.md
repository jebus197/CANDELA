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

### Snapshot current state
```bash
git checkout main && git pull
git tag -a v0.2-draft -m "Stable before validator refactor"
git branch backup/v0.2-draft
git push origin main v0.2-draft backup/v0.2-draft
