"""
Scan CSIRO contest package for absolute import tier violations (level_M with M >= K).

Allows relative imports within a level (forbid_relative_in_logic=False). Fails if any
CONTEST_UPWARD violations are found.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit import run_csiro_level_violations_cli_api


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=_SCRIPTS_ROOT,
        help="Scripts root containing layers/ (default: parent of dev/)",
    )
    parser.add_argument(
        "--contest-root",
        type=Path,
        default=None,
        help="Override path to .../contests/level_csiro/",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write markdown report here (default: workspace .cursor/audit-results/contests/audits)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for report filename (default: today)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Write violations JSON next to the .md report",
    )
    args = parser.parse_args()
    env = run_csiro_level_violations_cli_api(
        {
            "scripts_dir": args.scripts_dir.resolve(),
            "contest_root": args.contest_root,
            "generated": args.date,
            "output_dir": args.output_dir.resolve() if args.output_dir else None,
            "write_json": args.json,
        }
    )
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 2
    data = env["data"]
    print(f"[OK] Wrote {data['md_path']}")
    if "json_path" in data:
        print(f"[OK] Wrote {data['json_path']}")
    print(data["summary_line"])
    return int(data["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
