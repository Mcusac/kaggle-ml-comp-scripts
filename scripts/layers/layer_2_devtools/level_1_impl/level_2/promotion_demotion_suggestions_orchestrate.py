"""
Orchestrate promotion/demotion suggestions (report-only).
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit import (
    run_promotion_demotion_suggestions_with_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_scripts_root = Path(__file__).resolve().parents[4]
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=default_scripts_root,
        help="Scripts root directory containing `layers/` (default: scripts/).",
    )
    parser.add_argument(
        "--scope",
        type=str,
        default="general",
        choices=("general", "contests", "infra"),
        help="Which tiering scheme to apply.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Scope root that contains `level_N/` directories (defaults depend on --scope).",
    )
    parser.add_argument(
        "--contest-slug",
        type=str,
        default="level_csiro",
        help="Contest slug under level_1_impl/ when scope=contests (default: level_csiro).",
    )
    parser.add_argument(
        "--include",
        type=Path,
        action="append",
        default=[],
        help="Include only files under this path (repeatable).",
    )
    parser.add_argument(
        "--exclude",
        type=Path,
        action="append",
        default=[],
        help="Exclude files under this path (repeatable).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Explicit output directory (default: workspace/.cursor/audit-results/<scope>/audits).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filename (default: today).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write JSON payload next to the markdown report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any promotion or demotion candidates are suggested.",
    )
    parser.add_argument(
        "--min-total-inbound",
        type=int,
        default=10,
        help="Heavy reuse threshold: minimum inbound edges (promotion).",
    )
    parser.add_argument(
        "--min-distinct-importers",
        type=int,
        default=5,
        help="Heavy reuse threshold: minimum distinct importer modules (promotion).",
    )
    parser.add_argument(
        "--min-distinct-levels",
        type=int,
        default=2,
        help="Heavy reuse threshold: minimum distinct importer levels (promotion).",
    )
    parser.add_argument(
        "--top-importers-limit",
        type=int,
        default=10,
        help="Max top importers listed per row.",
    )
    args = parser.parse_args()

    scripts_root = args.scripts_dir.resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()

    if args.root is not None:
        root = args.root.resolve()
    else:
        if args.scope == "general":
            root = (scripts_root / "layers" / "layer_0_core").resolve()
        elif args.scope == "infra":
            root = (
                scripts_root / "layers" / "layer_1_competition" / "level_0_infra"
            ).resolve()
        else:
            root = (
                scripts_root
                / "layers"
                / "layer_1_competition"
                / "level_1_impl"
                / args.contest_slug
            ).resolve()

    if args.scope == "general":
        import_prefixes = ["layers.layer_0_core."]
    elif args.scope == "contests":
        import_prefixes = [f"layers.layer_1_competition.contests.{args.contest_slug}."]
    else:
        import_prefixes = ["layers.layer_1_competition.level_0_infra."]

    env = run_promotion_demotion_suggestions_with_artifacts(
        {
            "scripts_dir": scripts_root,
            "scope": args.scope,
            "root": root,
            "generated": generated,
            "include": [p.resolve() for p in args.include],
            "exclude": [p.resolve() for p in args.exclude],
            "write_json": bool(args.json),
            "output_dir": args.output_dir.resolve() if args.output_dir else None,
            "strict": bool(args.strict),
            "import_prefixes": import_prefixes,
            "heavy_reuse_policy": {
                "min_total_inbound": int(args.min_total_inbound),
                "min_distinct_importers": int(args.min_distinct_importers),
                "min_distinct_levels": int(args.min_distinct_levels),
            },
            "top_importers_limit": int(args.top_importers_limit),
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    data = env["data"]
    print(f"[OK] Wrote {data['md_path']}")
    if "json_path" in data:
        print(f"[OK] Wrote {data['json_path']}")
    print(data["summary_line"])
    code = int(data.get("exit_code", 0) or 0)
    if code:
        raise SystemExit(code)


if __name__ == "__main__":
    main()

