"""
Barrel enforcement: merged general stack + contest + competition-infra import scans.

Writes ``barrel_enforcement_scan_<date>.{md,json}`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON ``schema: barrel_enforcement_scan.v1``).
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

_MODULE = Path(__file__).resolve()
_SCRIPTS = _MODULE.parents[4]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from layers.layer_2_devtools.level_1_impl.level_1 import api_audit


def _defaults() -> tuple[Path, Path, Path]:
    """``scripts`` root, ``layer_0_core``, infra ``level_0`` (under ``level_0_infra``)."""
    root = _SCRIPTS
    layers = root / "layers"
    layer_0_core = layers / "layer_0_core"
    infra_0 = layers / "layer_1_competition" / "level_0_infra" / "level_0"
    return root, layer_0_core, infra_0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    d_root, d_core, d_infra = _defaults()
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=d_root,
        help="Directory that contains `layers/` (default: kaggle-ml-comp-scripts/scripts).",
    )
    parser.add_argument(
        "--layer-0-core",
        type=Path,
        default=None,
        help="General stack root (default: <scripts-dir>/layers/layer_0_core).",
    )
    parser.add_argument(
        "--contest-root",
        type=Path,
        default=None,
        help="Contest package (default: .../level_1_competition/level_1_impl/level_csiro).",
    )
    parser.add_argument(
        "--contest-slug",
        type=str,
        default="level_csiro",
        help="Directory name under level_1_impl when --contest-root is omitted (default: level_csiro).",
    )
    parser.add_argument(
        "--infra-level-0",
        type=Path,
        default=None,
        help="Competition infra `level_0` root (default: .../level_0_infra/level_0).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write reports here (default: <workspace>/.cursor/audit-results/general/audits).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filenames (default: today).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Write barrel_enforcement_scan_<date>.json next to the .md file.",
    )
    parser.add_argument(
        "--skip-general",
        action="store_true",
        help="Omit layer_0_core scan (merged rows from general will be empty).",
    )
    parser.add_argument(
        "--skip-contest",
        action="store_true",
        help="Omit contest tier scan.",
    )
    parser.add_argument(
        "--skip-infra",
        action="store_true",
        help="Omit competition infra scan.",
    )
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit with code 1 if violation_count exceeds --max-violations (default 0).",
    )
    parser.add_argument(
        "--max-violations",
        type=int,
        default=0,
        help="When using --fail-on-violations, allow up to this many violations (default: 0).",
    )
    parser.add_argument(
        "--fail-on-parse-errors",
        action="store_true",
        help="Exit 1 if any file failed to parse in any included scan.",
    )
    args = parser.parse_args()
    scripts = args.scripts_dir.resolve()
    layer_core = (args.layer_0_core or d_core).resolve()
    cr = args.contest_root
    contest_root = (
        cr.resolve()
        if cr
        else (scripts / "layers" / "layer_1_competition" / "level_1_impl" / args.contest_slug)
    ).resolve()
    infra = (args.infra_level_0 or d_infra).resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()

    env = api_audit.run_barrel_enforcement_with_artifacts(
        {
            "scripts_dir": scripts,
            "layer_0_core": layer_core,
            "contest_root": contest_root,
            "contest_slug": str(args.contest_slug),
            "infra_level_0": infra,
            "generated": generated,
            "output_dir": args.output_dir.resolve() if args.output_dir else None,
            "write_json": bool(args.json),
            "run_general": not args.skip_general,
            "run_contest": not args.skip_contest,
            "run_infra": not args.skip_infra,
        }
    )
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 2
    data = env["data"]
    print(f"✅ [OK] Wrote {data['md_path']}")
    if "json_path" in data:
        print(f"✅ [OK] Wrote {data['json_path']}")
    print(data["summary_line"])
    exit_code = 0
    if args.fail_on_violations:
        max_v = max(0, int(args.max_violations))
        vcount = int(data.get("violation_count", 0))
        if vcount > max_v:
            print(
                f"❌ [FAIL] violation_count={vcount} exceeds --max-violations={max_v}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_parse_errors and int(data.get("parse_error_count", 0)) > 0:
        print(
            f"❌ [FAIL] parse_error_count={data.get('parse_error_count')}",
            file=sys.stderr,
        )
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
