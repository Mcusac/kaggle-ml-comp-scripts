#!/usr/bin/env python3
"""
Emit deterministic audit target queues (orchestrator Step 1e).

Run from scripts/:  python dev/scripts/audit_targets.py ...
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_discovery import run_audit_targets_cli_complete


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )


def main() -> int:
    _win_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preset",
        choices=("comprehensive",),
        default="comprehensive",
        help="Target discovery preset (default: comprehensive = Step 1e)",
    )
    parser.add_argument(
        "--layers-root",
        type=Path,
        default=None,
        help="Path to scripts/layers (default: <scripts>/layers)",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Repo root with .cursor/audit-results (default: discover)",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Print markdown table to stdout (after JSON if both)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print only JSON",
    )
    parser.add_argument(
        "--write-manifest",
        type=Path,
        default=None,
        help="Write queue JSON to this path (parent dirs created)",
    )
    args = parser.parse_args()
    env = run_audit_targets_cli_complete(
        {
            "scripts_root": _SCRIPTS_ROOT,
            "preset": args.preset,
            "layers_root": args.layers_root,
            "workspace_root": args.workspace_root,
            "markdown": args.markdown,
            "json_only": args.json_only,
            "write_manifest": args.write_manifest,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    data = env["data"]
    for line in data["stderr_messages"]:
        print(line, file=sys.stderr)
    print(data["json_text"])
    if data["print_markdown_after"] and data.get("markdown"):
        print()
        print(data["markdown"], end="")
    return int(data["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
