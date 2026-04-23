"""Public API: audit checks not covered by api_audit (circular deps, dead symbols)."""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path
from types import ModuleType
from typing import Any
import sys

_MODULE = Path(__file__).resolve()
_SCRIPTS_ROOT = _MODULE.parents[4]


def _ensure_pkg(mod_name: str, pkg_path: Path) -> None:
    if mod_name in sys.modules:
        return
    m = ModuleType(mod_name)
    m.__path__ = [str(pkg_path)]
    sys.modules[mod_name] = m


# Avoid importing package `__init__.py` aggregators (they can pull optional deps).
_ensure_pkg("layers", _SCRIPTS_ROOT / "layers")
_ensure_pkg("layers.layer_2_devtools", _SCRIPTS_ROOT / "layers" / "layer_2_devtools")
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra",
    _SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_0_infra",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_1_impl",
    _SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_1_impl.level_2",
    _SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl" / "level_2",
)


def _load_module_from_path(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ENVELOPE_MOD: Any = None


def _get_envelope() -> Any:
    global _ENVELOPE_MOD
    if _ENVELOPE_MOD is not None:
        return _ENVELOPE_MOD
    ep = (
        _MODULE.parents[2]
        / "level_0_infra"
        / "level_0"
        / "contracts"
        / "envelope.py"
    )
    _ENVELOPE_MOD = _load_module_from_path("devtools_envelope_api_audit_checks", ep)
    return _ENVELOPE_MOD


_e = _get_envelope()
_err = _e.err
_ok = _e.ok
_parse_generated_optional = _e.parse_generated_optional

_CIRCULAR_DEPS_MOD: Any = None
_DEAD_SYMBOL_MOD: Any = None


def _get_circular_deps_mod() -> Any:
    global _CIRCULAR_DEPS_MOD
    if _CIRCULAR_DEPS_MOD is not None:
        return _CIRCULAR_DEPS_MOD
    p = Path(__file__).resolve().parent.parent / "level_2" / "circular_deps.py"
    _CIRCULAR_DEPS_MOD = _load_module_from_path("devtools_circular_deps_api", p)
    return _CIRCULAR_DEPS_MOD


def _get_dead_symbol_mod() -> Any:
    global _DEAD_SYMBOL_MOD
    if _DEAD_SYMBOL_MOD is not None:
        return _DEAD_SYMBOL_MOD
    p = Path(__file__).resolve().parent.parent / "level_2" / "dead_symbol_detector.py"
    _DEAD_SYMBOL_MOD = _load_module_from_path("devtools_dead_symbol_detector_api", p)
    return _DEAD_SYMBOL_MOD


def run_circular_deps_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Run circular dependency scan and write artifacts.

    Config:
      - root: Path-like (optional; default scripts_root)
      - scripts_root: Path-like (optional; used for default root when root is omitted)
      - output_dir: Path-like (optional; default workspace/.cursor/audit-results/general/audits)
      - generated: date or YYYY-MM-DD (optional; default today)
      - include_tests: bool (default False)
      - write_json: bool (default False)

    Returns:
        Envelope; on success data has md_path, optional json_path, cycle_count, parse_error_count.
    """
    try:
        mod = _get_circular_deps_mod()

        scripts_root = Path(config.get("scripts_root") or "").resolve() if config.get("scripts_root") else None
        root = Path(config.get("root") or (scripts_root if scripts_root else mod._SCRIPTS)).resolve()
        gen = _parse_generated_optional(config.get("generated")) or date.today()

        workspace = mod.resolve_workspace_root(root)
        out_dir = (
            Path(config["output_dir"]).resolve()
            if config.get("output_dir")
            else (workspace / ".cursor" / "audit-results" / "general" / "audits")
        )
        include_tests = bool(config.get("include_tests", False))
        write_json = bool(config.get("write_json", False))

        graph, parse_error_count = mod._build_internal_import_graph(
            root=root, include_tests=include_tests
        )
        components = mod.find_cycles(graph)
        findings = [
            mod.CycleFinding(
                nodes=sorted(comp),
                chain=mod._cycle_chain_for_component(component=comp, graph=graph),
            )
            for comp in components
        ]
        findings.sort(key=lambda c: (len(c.nodes), c.nodes))

        paths = mod._write_artifacts(
            workspace=workspace,
            output_dir=out_dir,
            generated=gen,
            root=root,
            parse_error_count=int(parse_error_count),
            cycles=findings,
            write_json=write_json,
        )
        return _ok(
            {
                "md_path": paths.get("md_path"),
                "json_path": paths.get("json_path"),
                "cycle_count": int(paths.get("cycle_count", 0)),
                "parse_error_count": int(parse_error_count),
                "root": root.as_posix(),
                "workspace": workspace.as_posix(),
            }
        )
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        return _err([str(exc)])


def run_dead_symbol_detector_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Run dead symbol detector (unreferenced + unreachable) and write artifacts.

    Config:
      - root: Path-like (optional; default scripts_root/layers/layer_0_core)
      - scripts_root: Path-like (required unless root provided)
      - config_path: optional Path-like JSON for DeadSymbolConfig.load()
      - output_dir: optional Path-like (default workspace/.cursor/audit-results/general/audits)
      - generated: date or YYYY-MM-DD (optional; default today)
      - include_tests: bool (default False)
      - write_json: bool (default False)

    Returns:
        Envelope; on success data has md_path, optional json_path, unreferenced_count, unreachable_count, etc.
    """
    try:
        mod = _get_dead_symbol_mod()

        root_arg = config.get("root")
        scripts_root_arg = config.get("scripts_root")
        if root_arg is None and scripts_root_arg is None:
            return _err(["root or scripts_root is required"])
        scripts_root = (
            Path(scripts_root_arg).resolve()
            if scripts_root_arg is not None
            else None
        )
        root = (
            Path(root_arg).resolve()
            if root_arg is not None
            else (scripts_root / "layers" / "layer_0_core").resolve()
        )
        if not root.exists():
            return _err([f"root does not exist: {root}"])

        gen = _parse_generated_optional(config.get("generated")) or date.today()
        workspace = mod.resolve_workspace_root(root)
        out_dir = (
            Path(config["output_dir"]).resolve()
            if config.get("output_dir")
            else (workspace / ".cursor" / "audit-results" / "general" / "audits")
        )
        include_tests = bool(config.get("include_tests", False))
        write_json = bool(config.get("write_json", False))
        cfg_path = Path(config["config_path"]).resolve() if config.get("config_path") else None

        cfg = mod.DeadSymbolConfig.load(cfg_path)
        payload = mod._compute_run_payload(
            root=root,
            include_tests=include_tests,
            config=cfg,
            generated=gen,
            workspace=workspace,
        )
        paths = mod._write_artifacts(output_dir=out_dir, payload=payload, write_json=write_json)

        return _ok(
            {
                "md_path": paths.get("md_path"),
                "json_path": paths.get("json_path"),
                "definition_count": int(paths.get("definition_count", 0)),
                "reference_count": int(paths.get("reference_count", 0)),
                "unreferenced_count": int(paths.get("unreferenced_count", 0)),
                "unreachable_count": int(paths.get("unreachable_count", 0)),
                "root": root.as_posix(),
                "workspace": workspace.as_posix(),
            }
        )
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        return _err([str(exc)])

