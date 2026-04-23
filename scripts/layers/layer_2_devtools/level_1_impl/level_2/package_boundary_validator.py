#!/usr/bin/env python3
"""Validate package boundaries and emit deterministic report artifacts."""

import argparse
import sys
import types
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

# Avoid importing `layers/__init__.py` (can be heavy / optional deps).
if "layers" not in sys.modules:
    pkg = types.ModuleType("layers")
    pkg.__path__ = [str(_SCRIPTS_ROOT / "layers")]
    sys.modules["layers"] = pkg
for name, rel in [
    ("layers.layer_2_devtools", ["layers", "layer_2_devtools"]),
    ("layers.layer_2_devtools.level_0_infra", ["layers", "layer_2_devtools", "level_0_infra"]),
    ("layers.layer_2_devtools.level_0_infra.level_0", ["layers", "layer_2_devtools", "level_0_infra", "level_0"]),
    ("layers.layer_2_devtools.level_1_impl", ["layers", "layer_2_devtools", "level_1_impl"]),
    ("layers.layer_2_devtools.level_1_impl.level_1", ["layers", "layer_2_devtools", "level_1_impl", "level_1"]),
]:
    if name not in sys.modules:
        p = types.ModuleType(name)
        p.__path__ = [str(_SCRIPTS_ROOT.joinpath(*rel))]
        sys.modules[name] = p

from layers.layer_2_devtools.level_1_impl.level_1.api_validation import (
    run_validate_package_boundaries_complete,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scripts-root",
        type=Path,
        default=_SCRIPTS_ROOT,
        help="Scripts root containing layers/ and dev/",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Workspace root (default: discover from scripts-root).",
    )
    parser.add_argument(
        "--scope-root",
        type=Path,
        default=None,
        help="Optional subtree root to limit scanning.",
    )
    parser.add_argument(
        "--no-include-dev",
        action="store_true",
        help="Do not scan scripts/dev.",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for report timestamp (default: today).",
    )
    parser.add_argument(
        "--output-base",
        type=Path,
        default=None,
        help="Optional output base path without extension.",
    )
    args = parser.parse_args()

    scripts_root = args.scripts_root.resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()

    env = run_validate_package_boundaries_complete(
        {
            "scripts_root": scripts_root,
            "include_dev": not bool(args.no_include_dev),
            "workspace_root": args.workspace_root,
            "scope_root": args.scope_root,
            "generated": generated,
            "output_base": args.output_base.resolve() if args.output_base else None,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    data = env["data"]
    print(f"[OK] Wrote {data['json_path']}")
    print(f"[OK] Wrote {data['md_path']}")
    print(data["summary_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

