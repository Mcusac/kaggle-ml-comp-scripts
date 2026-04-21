#!/usr/bin/env python3
"""
Validate per-level audit artifact schema under .cursor/audit-results.

Checks:
- Canonical metadata keys: audit_scope, level_name, pass_number
- Required audit result sections in *_audit.md files
"""

import argparse
import importlib.util
import io
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

from layers.layer_2_devtools.level_1_impl.level_2.audit_artifact_bootstrap import (
    get_resolve_audit_artifact_root,
)

_precheck_validate_fn: Callable[[dict[str, Any]], list[str]] | None = None


def _validate_precheck_json(data: dict[str, Any]) -> list[str]:
    """Load ``precheck_json_contract`` by file path (no ``layers.*`` package import)."""
    global _precheck_validate_fn
    if _precheck_validate_fn is None:
        contract_path = (
            Path(__file__).resolve().parent.parent.parent
            / "level_0_infra"
            / "level_0"
            / "models"
            / "precheck_json_contract.py"
        )
        name = "precheck_json_contract_standalone"
        spec = importlib.util.spec_from_file_location(name, contract_path)
        if spec is None or spec.loader is None:
            return [f"cannot load precheck contract from {contract_path}"]
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _precheck_validate_fn = mod.validate_precheck_json
    return _precheck_validate_fn(data)


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

    ws = get_resolve_audit_artifact_root()(Path.cwd())
    if not (ws / ".cursor" / "audit-results").is_dir():
        raise ValueError(
            "could not locate artifact_base containing .cursor/audit-results "
            f"(cwd={Path.cwd()})"
        )
    return ws


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
        help="Artifact root directory (e.g. input/kaggle-ml-comp-scripts) containing .cursor/audit-results",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when legacy keys scope/level/pass are present",
    )
    parser.add_argument(
        "--precheck-summaries",
        action="store_true",
        help=(
            "Validate precheck_*.json files under each scope's summaries/ "
            "using precheck_json_contract (use with --strict to fail on skipped_machine_script stubs)"
        ),
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

    if args.precheck_summaries:
        for scope in scopes:
            summaries = root / scope / "summaries"
            if not summaries.is_dir():
                print(f"⚠️ missing summaries directory: {summaries}")
                continue
            for pj in sorted(summaries.glob("precheck_*.json")):
                total_checked += 1
                try:
                    data = json.loads(_read_text(pj))
                except json.JSONDecodeError as exc:
                    total_errors += 1
                    print(f"❌ {pj}\n  - invalid JSON: {exc}")
                    continue
                verr = _validate_precheck_json(data)
                if verr:
                    total_errors += 1
                    print(f"❌ {pj}")
                    for err in verr:
                        print(f"  - {err}")
                    continue
                if args.strict and data.get("precheck_status") == "skipped_machine_script":
                    total_errors += 1
                    print(f"❌ {pj}\n  - strict: precheck_status is skipped_machine_script")
                    continue
                print(f"✅ {pj}")
        if total_checked == 0:
            print("⚠️ no precheck_*.json files under summaries/")
            return 1
        if total_errors:
            print(f"❌ precheck JSON check failed: {total_errors}/{total_checked} files")
            return 1
        print(f"✅ precheck JSON check passed: {total_checked} files")
        return 0

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
