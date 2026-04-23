#!/usr/bin/env python3
"""Write `check_health --json` output to a file (CI-friendly).

Run from `input/kaggle-ml-comp-scripts/scripts/`::

  python -m layers.layer_2_devtools.level_1_impl.level_2.write_health_report \
    --root ".." \
    --output "../health_report.json"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_health import (  # noqa: E402
    run_package_health_cli_api,
)


def main() -> int:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True, help="Root of the tree to analyze.")
    p.add_argument(
        "--output",
        type=Path,
        required=True,
        help="JSON file path to write (parents created as needed).",
    )
    p.add_argument("--config", type=Path, default=None, help="Optional health config JSON.")
    args = p.parse_args()

    env = run_package_health_cli_api(
        {
            "root": args.root.resolve(),
            "as_json": True,
            "threshold_config_path": args.config.resolve() if args.config else None,
        }
    )
    if env["status"] != "ok":
        print("\n".join(env.get("errors") or ["unknown error"]), file=sys.stderr)
        return 1

    report_text = str(env["data"]["report"])
    try:
        payload = json.loads(report_text)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"❌ health json parse error: {exc}", file=sys.stderr)
        return 1

    out = args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"✅ [OK] Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

