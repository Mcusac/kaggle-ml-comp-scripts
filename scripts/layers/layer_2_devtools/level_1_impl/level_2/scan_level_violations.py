"""
Scan general stack level_0 .. level_10 for import layering violations.

Read-only: writes a markdown report under .cursor/audit-results/general/audits/.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit import run_general_stack_scan_with_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_scripts = (
        Path(__file__).resolve().parent.parent / "layers" / "layer_0_core"
    )
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=default_scripts,
        help=(
            "Directory containing level_0 .. level_10 "
            "(default: scripts/layers/layer_0_core)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Markdown report path (default: .cursor/audit-results/general/audits/)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filename (default: today)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write level_violations_scan_<date>.json next to the .md report",
    )
    args = parser.parse_args()
    scripts_dir = args.scripts_dir.resolve()

    generated = date.fromisoformat(args.date) if args.date else date.today()
    env = run_general_stack_scan_with_artifacts(
        {
            "scripts_dir": scripts_dir,
            "generated": generated,
            "output": args.output,
            "write_json": args.json,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    data = env["data"]
    print(f"[OK] Wrote {data['md_path']}")
    if "json_path" in data:
        print(f"[OK] Wrote {data['json_path']}")
    print(data["summary_line"])


if __name__ == "__main__":
    main()
