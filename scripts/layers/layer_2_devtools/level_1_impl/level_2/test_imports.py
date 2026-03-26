"""
Comprehensive import test suite entrypoint.

Run: python dev/tests/test_imports.py [--verbose]
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

from layers.layer_2_devtools.level_1_impl.level_1.api_import_probe import (
    run_import_test_suite_cli_api,
)


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
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    env = run_import_test_suite_cli_api(
        {"scripts_root": _SCRIPTS_ROOT, "verbose": args.verbose}
    )
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
