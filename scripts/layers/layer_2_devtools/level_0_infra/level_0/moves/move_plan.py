from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import file_to_module


@dataclass(frozen=True)
class MoveSpec:
    root: Path
    src_path: Path | None = None
    src_module: str | None = None
    dest_level: int | None = None
    dest_path: Path | None = None


@dataclass(frozen=True)
class MovePlan:
    root: Path
    src_path: Path
    dest_path: Path
    old_module: str
    new_module: str

    @property
    def affected_init_roots(self) -> list[Path]:
        # Minimal barrel regen scope: old and new parent packages.
        return sorted({self.src_path.parent, self.dest_path.parent}, key=lambda p: p.as_posix())


class MovePlanError(ValueError):
    pass


def compute_move_plan(*, spec: MoveSpec) -> MovePlan:
    root = spec.root.resolve()
    if not root.is_dir():
        raise MovePlanError(f"root is not a directory: {root.as_posix()}")

    if spec.src_path is None and spec.src_module is None:
        raise MovePlanError("Either src_path or src_module is required.")
    if spec.src_path is not None and spec.src_module is not None:
        raise MovePlanError("Provide only one of src_path or src_module.")

    if spec.dest_path is None and spec.dest_level is None:
        raise MovePlanError("Either dest_path or dest_level is required.")
    if spec.dest_path is not None and spec.dest_level is not None:
        raise MovePlanError("Provide only one of dest_path or dest_level.")

    src_path = _resolve_src_path(root=root, src_path=spec.src_path, src_module=spec.src_module)
    dest_path = _resolve_dest_path(root=root, src_path=src_path, dest_path=spec.dest_path, dest_level=spec.dest_level)

    if dest_path.exists():
        raise MovePlanError(f"destination already exists: {dest_path.as_posix()}")

    old_module = _module_from_file(root=root, path=src_path)
    new_module = _module_from_file(root=root, path=dest_path)
    return MovePlan(
        root=root,
        src_path=src_path,
        dest_path=dest_path,
        old_module=old_module,
        new_module=new_module,
    )


def _resolve_src_path(*, root: Path, src_path: Path | None, src_module: str | None) -> Path:
    if src_path is not None:
        p = src_path.resolve()
    else:
        # module path relative to root
        mod = str(src_module or "").strip()
        if not mod:
            raise MovePlanError("src_module is empty.")
        p = (root / Path(*mod.split("."))).with_suffix(".py")
        if not p.exists():
            init = (root / Path(*mod.split(".")) / "__init__.py").resolve()
            if init.exists():
                p = init
    try:
        p.relative_to(root)
    except ValueError:
        raise MovePlanError(f"src is not under root: src={p.as_posix()} root={root.as_posix()}")
    if not p.is_file():
        raise MovePlanError(f"src is not a file: {p.as_posix()}")
    return p


def _resolve_dest_path(*, root: Path, src_path: Path, dest_path: Path | None, dest_level: int | None) -> Path:
    if dest_path is not None:
        p = dest_path.resolve()
        try:
            p.relative_to(root)
        except ValueError:
            raise MovePlanError(f"dest is not under root: dest={p.as_posix()} root={root.as_posix()}")
        return p

    level = dest_level
    if level is None or int(level) < 0:
        raise MovePlanError(f"dest_level must be >= 0, got: {dest_level}")
    src_rel = src_path.relative_to(root)
    parts = list(src_rel.parts)
    idx = _find_level_dir_index(parts)
    if idx is None:
        raise MovePlanError(f"src is not under a level_N directory: {src_rel.as_posix()}")
    parts[idx] = f"level_{int(level)}"
    return (root / Path(*parts)).resolve()


def _find_level_dir_index(parts: list[str]) -> int | None:
    for i, p in enumerate(parts):
        if p.startswith("level_") and p[6:].isdigit():
            return i
    return None


def _module_from_file(*, root: Path, path: Path) -> str:
    mod = file_to_module(path, root)
    if mod is None:
        raise MovePlanError(f"unable to compute module from path: {path.as_posix()}")
    return mod

