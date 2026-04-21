#!/usr/bin/env python3
"""
Verify hyperparameter recommendations against existing metadata.

Checks for duplicates, validates parameter ranges, and ensures recommendations
are properly formatted and don't conflict with existing tested values.

Usage:
  From scripts/:       python -m layers.layer_2_devtools.level_1_impl.level_2.verify_hyperparameter_recommendations --model-type lgbm --recommendations FILE [--metadata-dir PATH]
  (Always run with cwd set to ``kaggle-ml-comp-scripts/scripts/`` for ``layers`` imports.)
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_hyperparameter import (
    run_verify_hyperparameter_recommendations_cli_api,
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
        description="Verify hyperparameter recommendations against existing metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--model-type",
        type=str,
        required=True,
        choices=["lgbm", "xgboost", "xgb", "ridge"],
        help="Type of regression model",
    )
    parser.add_argument(
        "--recommendations",
        type=Path,
        required=True,
        help="Path to recommendations JSON file",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=None,
        help="Path to metadata directory (auto-detected if not provided)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    env = run_verify_hyperparameter_recommendations_cli_api(
        {
            "model_type": args.model_type,
            "recommendations_path": args.recommendations,
            "metadata_dir": args.metadata_dir,
            "as_json": args.json,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}")
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
