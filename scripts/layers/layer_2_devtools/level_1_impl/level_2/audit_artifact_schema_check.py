#!/usr/bin/env python3
"""
Validate per-level audit artifact schema under .cursor/audit-results.

Checks:
- Canonical metadata keys: audit_scope, level_name, pass_number
- Required audit result sections in *_audit.md files
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

CANONICAL_KEYS = ("audit_scope:", "level_name:", "pass_number:")
LEGACY_KEYS = ("scope:", "level:", "pass:")
REQUIRED_SECTIONS = (
    "=== AUDIT RESULT:",
    "PUBLIC API (post-audit):",
    "CONSOLIDATED CHANGE LOG:",
    "CALLERS TOUCHED (Phase 8):",
    "VIOLATIONS REQUIRING HUMAN REVIEW:",
    "ITEMS FOR HUMAN JUDGMENT:",
    "=== END AUDIT RESULT:",
)
PER_LEVEL_PATTERN = re.compile(
    r"^(?:level_\d+|level_[a-z0-9_]+_level_\d+|level_[a-z0-9_]+_root|layer_Z_unsorted)_audit\.md$"
)


def _resolve_workspace(explicit_root: str | None) -> Path:
    if explicit_root:
        root = Path(explicit_root).resolve()
        if (root / ".cursor" / "audit-results").is_dir():
            return root
        raise ValueError(f"root has no .cursor/audit-results: {root}")

    start = Path.cwd().resolve()
    for parent in (start, *start.parents):
        results_dir = parent / ".cursor" / "audit-results"
        if not results_dir.is_dir():
            continue
        has_expected_scope = any(
            (results_dir / scope / "audits").is_dir()
            for scope in ("general", "competition_infra", "contests_special")
        )
        if has_expected_scope:
            return parent
    raise ValueError("could not locate workspace root containing .cursor/audit-results")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _check_file(path: Path, strict: bool) -> list[str]:
    text = _read_text(path)
    errors: list[str] = []

    for key in CANONICAL_KEYS:
        if key not in text:
            errors.append(f"missing metadata key `{key[:-1]}`")

    if strict:
        for key in LEGACY_KEYS:
            if re.search(rf"(?m)^\s*{re.escape(key)}\s*", text):
                errors.append(f"legacy metadata key `{key[:-1]}` present in strict mode")

    for marker in REQUIRED_SECTIONS:
        if marker not in text:
            errors.append(f"missing result section `{marker}`")

    return errors


def main() -> int:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        choices=("general", "competition_infra", "contests_special"),
        default=None,
        help="Validate one scope only (default: all three scopes)",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Workspace root containing .cursor/audit-results",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when legacy keys scope/level/pass are present",
    )
    args = parser.parse_args()

    try:
        workspace = _resolve_workspace(args.root)
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1

    scopes = (args.scope,) if args.scope else ("general", "competition_infra", "contests_special")
    root = workspace / ".cursor" / "audit-results"
    total_checked = 0
    total_errors = 0

    for scope in scopes:
        audits_dir = root / scope / "audits"
        if not audits_dir.is_dir():
            print(f"⚠️ missing audits directory: {audits_dir}")
            continue

        files = sorted(audits_dir.glob("*_audit.md"))
        per_level_files = [p for p in files if PER_LEVEL_PATTERN.match(p.name)]
        print(f"🚀 scope={scope} files={len(per_level_files)}")

        for path in per_level_files:
            total_checked += 1
            errors = _check_file(path, strict=args.strict)
            if errors:
                total_errors += 1
                print(f"❌ {path}")
                for err in errors:
                    print(f"  - {err}")
            else:
                print(f"✅ {path}")

    if total_checked == 0:
        print("⚠️ no per-level audit files matched validation pattern")
        return 1

    if total_errors:
        print(f"❌ schema check failed: {total_errors}/{total_checked} files invalid")
        return 1

    print(f"✅ schema check passed: {total_checked} files valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
