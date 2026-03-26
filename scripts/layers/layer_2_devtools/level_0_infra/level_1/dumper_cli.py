import argparse
import sys
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0 import PackageDumper


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dump package directory trees to text file(s).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--root", type=Path)
    parser.add_argument("--dirs", nargs="+", type=Path)

    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("package_dumps"),
    )

    parser.add_argument("--multi", action="store_true")

    parser.add_argument(
        "--ext",
        default=".py",
        help="Comma separated file extensions",
    )

    args = parser.parse_args()

    if args.root is None and not args.dirs:
        parser.error("Provide either --root or --dirs")

    if args.root and args.dirs:
        parser.error("Use either --root or --dirs")

    if not args.multi and not args.output:
        parser.error("Single file mode requires --output")

    if args.multi and args.output:
        parser.error("Use --output-dir with --multi")

    save_mode = "multi_file" if args.multi else "single_file"

    extensions = {s.strip() for s in args.ext.split(",") if s.strip()}

    if args.root:
        dumper = PackageDumper(
            traversal="recursive",
            save_mode=save_mode,
            root_dir=args.root,
            output_file=args.output,
            output_dir=args.output_dir,
            file_extensions=extensions,
        )

    else:
        dumper = PackageDumper(
            traversal="explicit",
            save_mode=save_mode,
            directories=args.dirs,
            output_file=args.output,
            output_dir=args.output_dir,
            file_extensions=extensions,
        )

    dumper.dump()

    return 0


if __name__ == "__main__":
    sys.exit(main())
