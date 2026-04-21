"""
Pre-upload validation script.

Comprehensive validation that catches import errors, missing type annotations,
and other structural issues before uploading to Kaggle.

Catches:
- ModuleNotFoundError (missing modules)
- ImportError (import failures)
- NameError (missing type annotations like Dict, Tuple, etc.)
- SyntaxError (syntax issues)

Usage:
    python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload
    python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload --verbose
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_pre_upload import (
    run_pre_upload_validation_cli_api,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate contest implementation modules before upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload
  python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload --verbose
        """,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show full tracebacks and detailed error messages",
    )
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=_SCRIPTS_ROOT,
        help="Path to scripts directory (default: this repository's scripts/)",
    )

    args = parser.parse_args()
    env = run_pre_upload_validation_cli_api(
        {
            "scripts_root": args.scripts_dir.resolve(),
            "verbose": args.verbose,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}")
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    sys.exit(main())
