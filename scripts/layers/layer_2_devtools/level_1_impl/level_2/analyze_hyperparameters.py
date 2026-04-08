#!/usr/bin/env python3
"""
Hyperparameter analysis tool for ML model tuning.

Analyzes grid search results to identify top performers, parameter trends,
and generate focused grid search recommendations.

Usage:
  From project root:  python scripts/dev/scripts/analyze_hyperparameters.py --model-type lgbm [--metadata-dir PATH] [--top-n 20] [--json] [--output FILE]
  From scripts/:      python dev/scripts/analyze_hyperparameters.py --model-type lgbm [--metadata-dir PATH] [--top-n 20] [--json] [--output FILE]
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_hyperparameter import (
    run_analyze_hyperparameters_cli_api,
)


def main() -> int:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    parser = argparse.ArgumentParser(
        description="Hyperparameter analysis tool for ML model tuning.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--model-type",
        type=str,
        required=True,
        choices=["lgbm", "xgboost", "xgb", "ridge"],
        help="Type of regression model to analyze",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=None,
        help="Path to metadata directory (auto-detected if not provided)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of top performers to analyze",
    )
    parser.add_argument(
        "--top-percentile",
        type=float,
        default=0.1,
        help="Top percentile for recommendations (0.1 = top 10%%)",
    )
    parser.add_argument(
        "--expansion-factor",
        type=float,
        default=1.2,
        help="Factor to expand ranges around top values",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path for recommendations JSON (optional)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full analysis in JSON format",
    )

    args = parser.parse_args()

    env = run_analyze_hyperparameters_cli_api(
        {
            "model_type": args.model_type,
            "metadata_dir": args.metadata_dir,
            "top_n": args.top_n,
            "top_percentile": args.top_percentile,
            "expansion_factor": args.expansion_factor,
            "output_path": args.output,
            "as_json": args.json,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}")
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
