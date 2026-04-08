"""Public API: thin script orchestration (cleanup, bootstrap, one-off fixers)."""

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok
from layers.layer_2_devtools.level_0_infra.level_0.fix.layer_core_import_rewrite import (
    run_layer_core_import_rewrite,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.unused_import_cleanup import (
    run_unused_import_cleanup,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.violation_fix_bundle import (
    run_violation_fix_bundle,
)
from layers.layer_2_devtools.level_0_infra.level_0.format.inventory_bootstrap_markdown import (
    bootstrap_markdown,
)
from layers.layer_2_devtools.level_0_infra.level_0.fs.pycache_cleanup import clean_pycache
from layers.layer_2_devtools.level_0_infra.level_0.package_dump.cli import main as _package_dump_main
from layers.layer_2_devtools.level_0_infra.level_0.package_dump.presets import dump_level as _dump_level_preset


def run_unused_import_cleanup_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``report``, ``root``, ``dry_run``."""
    try:
        rep = config.get("report")
        if rep is None:
            return err(["report is required"])
        rc = run_unused_import_cleanup(
            report=Path(rep),
            root=Path(config.get("root", Path.cwd())),
            dry_run=bool(config.get("dry_run", False)),
        )
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_clean_pycache_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``root``, ``dry_run``, ``remove_pyc_files``."""
    try:
        root = Path(config.get("root", Path.cwd()))
        if not root.is_dir():
            return err([f"root is not a directory: {root}"])
        dry = bool(config.get("dry_run", False))
        result = clean_pycache(
            root,
            dry_run=dry,
            remove_pyc_files=bool(config.get("remove_pyc_files", False)),
        )
        if dry:
            msg = (
                f"Dry run: would remove {result.dirs_removed} __pycache__ dirs and "
                f"{result.files_removed} .pyc files."
            )
        else:
            msg = (
                f"Removed {result.dirs_removed} __pycache__ dirs and "
                f"{result.files_removed} .pyc files."
            )
        return ok({"exit_code": 0, "message": msg})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_inventory_bootstrap_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``level_path``, optional ``workspace_root``, ``output`` (Path or None)."""
    try:
        lp = config.get("level_path")
        if lp is None:
            return err(["level_path is required"])
        ws = Path(config["workspace_root"]).resolve() if config.get("workspace_root") else None
        body = bootstrap_markdown(Path(lp), ws)
        out = config.get("output")
        wrote = False
        if out:
            outp = Path(out)
            outp.parent.mkdir(parents=True, exist_ok=True)
            outp.write_text(body, encoding="utf-8")
            wrote = True
        return ok({"body": body, "output_path": str(out) if out else None, "wrote_file": wrote})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_layer_core_import_rewrite_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: optional ``layer_0_core`` Path (default: scripts_root/layers/layer_0_core)."""
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return err(["scripts_root is required"])
        core = config.get("layer_0_core")
        scripts_root = Path(sr)
        target = Path(core).resolve() if core else (scripts_root / "layers" / "layer_0_core")
        rc = run_layer_core_import_rewrite(target)
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_violation_fix_bundle_standalone_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``scripts_dev_dir``, ``apply`` (bool)."""
    try:
        sdd = config.get("scripts_dev_dir")
        if sdd is None:
            return err(["scripts_dev_dir is required"])
        dry_run = not bool(config.get("apply", False))
        run_violation_fix_bundle(Path(sdd), dry_run)
        return ok({})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_package_dump_sys_argv_api(argv: list[str]) -> dict[str, Any]:
    """Invoke package dump CLI with a replacement ``sys.argv`` (excluding prog)."""
    import sys

    old = sys.argv
    try:
        sys.argv = [old[0], *argv]
        rc = _package_dump_main()
        return ok({"exit_code": int(rc)})
    except SystemExit as exc:  # argparse may raise
        code = exc.code
        if isinstance(code, int):
            return ok({"exit_code": code})
        return err([str(code) if code else "package_dump exited"])
    finally:
        sys.argv = old


def run_dump_level_preset_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``level_name``, ``scripts_root``, optional ``output_dir`` (default package_dumps)."""
    try:
        name = config.get("level_name")
        sr = config.get("scripts_root")
        if name is None or sr is None:
            return err(["level_name and scripts_root are required"])
        layer0 = Path(sr) / "layers" / "layer_0_core"
        od = Path(config.get("output_dir", "package_dumps"))
        _dump_level_preset(str(name), scripts_root=layer0, output_dir=od)
        return ok({})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_verify_imports_stub_api(config: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG001
    """Placeholder integration point for future import verification."""
    return ok(
        {
            "lines": [
                "Import verification integration point.",
                "Scans all Python files and validates import statements.",
            ]
        }
    )


__all__ = [
    "run_clean_pycache_cli_api",
    "run_dump_level_preset_cli_api",
    "run_inventory_bootstrap_cli_api",
    "run_layer_core_import_rewrite_cli_api",
    "run_package_dump_sys_argv_api",
    "run_unused_import_cleanup_cli_api",
    "run_verify_imports_stub_api",
    "run_violation_fix_bundle_standalone_cli_api",
]
