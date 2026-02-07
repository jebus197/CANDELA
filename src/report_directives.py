#!/usr/bin/env python3
"""
Deterministic directive inventory report for reviewers.

Why this exists:
- Reviewers often (rightly) ask "how many directives exist, and how many are machine-checkable?"
- This script answers that from the canonical schema file, with stable ordering.

It does NOT modify any files and does NOT require network access.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEFAULT_SCHEMA_PATH = (Path(__file__).resolve().parents[1] / "src" / "directives_schema.json")


def _load_directives(schema_path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(schema_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "directives" in raw:
        directives = raw["directives"]
    else:
        directives = raw

    if not isinstance(directives, list):
        raise TypeError(f"Expected a list of directives, got: {type(directives).__name__}")

    out: List[Dict[str, Any]] = []
    for i, item in enumerate(directives):
        if not isinstance(item, dict):
            raise TypeError(f"Directive at index {i} is not an object/dict (got {type(item).__name__}).")
        out.append(item)
    return out


def _directive_key(d: Dict[str, Any]) -> Tuple[int, str]:
    # Stable ordering: numeric id then optional sub ("a", "b", ...). Missing sub sorts first.
    did = d.get("id")
    if not isinstance(did, int):
        # Keep unknown/malformed ids at the end but deterministic.
        return (10**9, str(did))
    sub = d.get("sub")
    if sub is None:
        sub_s = ""
    else:
        sub_s = str(sub)
    return (did, sub_s)


def _display_id(d: Dict[str, Any]) -> str:
    did = d.get("id")
    sub = d.get("sub")
    if isinstance(did, int) and sub:
        return f"{did}{sub}"
    return str(did)


def _has_na_validation(d: Dict[str, Any]) -> bool:
    vc = d.get("validation_criteria")
    return isinstance(vc, str) and vc.strip().upper() == "N/A"


def _has_real_validation(d: Dict[str, Any]) -> bool:
    vc = d.get("validation_criteria")
    if vc is None:
        return False
    if isinstance(vc, str) and vc.strip().upper() == "N/A":
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print exact directive counts and an ID/title list from directives_schema.json."
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Path to directives_schema.json (default: <repo>/src/directives_schema.json)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    schema_path = Path(args.path).expanduser().resolve()
    directives = _load_directives(schema_path)
    directives_sorted = sorted(directives, key=_directive_key)

    total_objects = len(directives_sorted)
    na_count = sum(1 for d in directives_sorted if _has_na_validation(d))
    real_count = sum(1 for d in directives_sorted if _has_real_validation(d))
    missing_count = total_objects - na_count - real_count

    # Unique numeric IDs are useful context when micro-directives exist.
    unique_numeric_ids = sorted({d["id"] for d in directives_sorted if isinstance(d.get("id"), int)})
    unique_numeric_id_count = len(unique_numeric_ids)

    rows = []
    for d in directives_sorted:
        did = _display_id(d)
        # Schema uses "text" (not "title") today. We keep a "title" label for reviewer convenience.
        title = str(d.get("title") or d.get("text") or "").strip()
        category = str(d.get("category") or "").strip()
        vc = d.get("validation_criteria")
        vc_kind = "N/A" if _has_na_validation(d) else ("REAL" if _has_real_validation(d) else "MISSING")
        rows.append(
            {
                "id": did,
                "title": title,
                "category": category,
                "validation": vc_kind,
                "validation_criteria": vc,
            }
        )

    if args.format == "json":
        payload = {
            "schema_path": str(schema_path),
            "total_directive_objects": total_objects,
            "unique_numeric_id_count": unique_numeric_id_count,
            "unique_numeric_ids": unique_numeric_ids,
            "validation_real": real_count,
            "validation_na": na_count,
            "validation_missing": missing_count,
            "directives": rows,
        }
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    # Text output (reviewer friendly).
    print(f"Schema: {schema_path}")
    print(f"Total directive objects: {total_objects}")
    print(f"Unique numeric IDs: {unique_numeric_id_count}")
    print(f'Validation criteria = "N/A": {na_count}')
    print(f"Validation criteria = REAL: {real_count}")
    print(f"Validation criteria = MISSING: {missing_count}")
    print()
    print("Directives (sorted):")
    for r in rows:
        cat = f'[{r["category"]}] ' if r.get("category") else ""
        print(f'- {r["id"]}: {cat}{r["title"]}  [validation={r["validation"]}]')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
