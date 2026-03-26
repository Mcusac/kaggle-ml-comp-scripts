#!/usr/bin/env python3
"""
Package health checker with comprehensive analysis.

Reports:
- File metrics: line counts, long functions, large classes
- Complexity: cyclomatic complexity for functions and classes
- Imports: dependency graph, deep imports, orphans
- Cohesion: internal vs external import ratio
- Duplication: code clone detection
- SOLID: principle violation detection
- Dead code: unused imports, unreachable code

Usage:
  From project root:  python scripts/dev/scripts/check_health.py [--root scripts] [--json] [--config FILE]
  From scripts/:      python dev/scripts/check_health.py [--root .] [--json] [--config FILE]

--root: Root of the tree to analyze (e.g. scripts when at project root to analyze only the framework).
Defaults: --root . (current directory)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_health import run_package_health_cli_api


def main() -> int:
    """Main entry point for package health analysis."""
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    default_root = Path.cwd()

    parser = argparse.ArgumentParser(
        description="Package health checker with comprehensive analysis.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--root", type=Path, default=default_root, help="Scripts root directory")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--config", type=Path, help="Threshold configuration file (JSON)")
    parser.add_argument("--no-complexity", action="store_true", help="Skip complexity analysis")
    parser.add_argument("--no-duplication", action="store_true", help="Skip duplication detection")
    parser.add_argument("--no-solid", action="store_true", help="Skip SOLID checks")
    parser.add_argument("--no-dead-code", action="store_true", help="Skip dead code detection")

    args = parser.parse_args()

    env = run_package_health_cli_api(
        {
            "root": args.root,
            "as_json": args.json,
            "threshold_config_path": args.config,
            "no_complexity": args.no_complexity,
            "no_duplication": args.no_duplication,
            "no_solid": args.no_solid,
            "no_dead_code": args.no_dead_code,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}")
        return 1

    print()
    print(env["data"]["report"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
