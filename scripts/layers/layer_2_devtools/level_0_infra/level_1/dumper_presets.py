from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0 import PackageDumper


def dump_level(
    level_name: str,
    *,
    scripts_root: Path,
    output_dir: Path | None = None,
) -> None:
    """Dump ``scripts_root / level_name`` into a single ``.txt`` under ``output_dir``."""
    root = scripts_root / level_name
    out_base = output_dir or Path("package_dumps")
    out_base.mkdir(parents=True, exist_ok=True)
    output = out_base / f"{level_name}_full_dump.txt"

    dumper = PackageDumper(
        traversal="recursive",
        save_mode="single_file",
        root_dir=root,
        output_file=output,
        file_extensions={".py"},
    )

    dumper.dump()
