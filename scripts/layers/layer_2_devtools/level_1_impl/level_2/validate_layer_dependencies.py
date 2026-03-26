#!/usr/bin/env python3
"""Validate layered dependency rules and emit deterministic report artifacts."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_validation import (
    run_validate_layer_dependencies_complete,
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

    env = run_validate_layer_dependencies_complete(
        {
            "scripts_root": scripts_root,
            "include_dev": True,
            "workspace_root": args.workspace_root,
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
