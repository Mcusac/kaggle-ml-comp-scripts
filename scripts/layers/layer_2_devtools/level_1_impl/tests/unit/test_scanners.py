"""Unit tests for layered scan operations."""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[5]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from layers.layer_2_devtools.level_1_impl.level_0.scan.contest_scan_ops import (
    scan_contest_package_file,
    scan_contest_root_directory,
)
from layers.layer_2_devtools.level_1_impl.level_0.scan.general_scan_ops import scan_general_stack_file
from layers.layer_2_devtools.level_1_impl.level_0.scan.infra_scan_ops import scan_infra_file
from layers.layer_2_devtools.level_1_impl.level_0.scan.special_scan_ops import scan_special_tree_file


def test_general_upward_violation(tmp_path: Path) -> None:
    core = tmp_path / "layer_0_core"
    f = core / "level_1" / "logic.py"
    f.parent.mkdir(parents=True)
    f.write_text("from level_3 import foo\n", encoding="utf-8")
    r = scan_general_stack_file(f, core)
    assert r.parse_error is None
    kinds = [v.kind for v in r.violations]
    assert "UPWARD" in kinds


def test_general_wrong_level(tmp_path: Path) -> None:
    core = tmp_path / "layer_0_core"
    f = core / "level_2" / "logic.py"
    f.parent.mkdir(parents=True)
    f.write_text("from level_2 import foo\n", encoding="utf-8")
    r = scan_general_stack_file(f, core)
    assert any(v.kind == "WRONG_LEVEL" for v in r.violations)


def test_general_allows_lower_level(tmp_path: Path) -> None:
    core = tmp_path / "layer_0_core"
    f = core / "level_4" / "logic.py"
    f.parent.mkdir(parents=True)
    f.write_text("from level_1 import foo\n", encoding="utf-8")
    r = scan_general_stack_file(f, core)
    assert not r.violations


def test_general_mixed_layer0_core_and_short_level(tmp_path: Path) -> None:
    """Explicit ``layers.layer_0_core`` imports must not mix with ``from level_N``."""
    core = tmp_path / "layer_0_core"
    f = core / "level_2" / "logic.py"
    f.parent.mkdir(parents=True)
    f.write_text(
        "from layers.layer_0_core.level_1 import a\n"
        "from level_0 import b\n",
        encoding="utf-8",
    )
    r = scan_general_stack_file(f, core)
    assert any(v.kind == "LAYER0_CORE_MIXED_IMPORT_STYLE" for v in r.violations)


def test_infra_tier_upward(tmp_path: Path) -> None:
    f = tmp_path / "infra" / "level_0" / "x.py"
    f.parent.mkdir(parents=True)
    f.write_text(
        "from layers.layer_1_competition.level_0_infra.level_2 import Thing\n",
        encoding="utf-8",
    )
    r = scan_infra_file(f, tier_k=0)
    assert any(v.kind == "INFRA_TIER_UPWARD" for v in r.violations)


def test_infra_barrel_deep_when_reexported(tmp_path: Path) -> None:
    infra = tmp_path / "level_0_infra"
    lv0 = infra / "level_0"
    lv0.mkdir(parents=True)
    (lv0 / "__init__.py").write_text(
        "from .reg import foo\n__all__ = (\"foo\",)\n",
        encoding="utf-8",
    )
    (lv0 / "reg.py").write_text("foo = 1\n", encoding="utf-8")
    f = infra / "level_2" / "x.py"
    f.parent.mkdir(parents=True)
    f.write_text(
        "from layers.layer_1_competition.level_0_infra.level_0.reg import foo\n",
        encoding="utf-8",
    )
    r = scan_infra_file(f, tier_k=2)
    assert any(v.kind == "INFRA_BARREL_DEEP" for v in r.violations)


def test_contest_allows_relative_when_disabled(tmp_path: Path) -> None:
    contest = tmp_path / "contests" / "level_demo"
    lev1 = contest / "level_1"
    f = lev1 / "a.py"
    f.parent.mkdir(parents=True)
    f.write_text("from .sibling import x\n", encoding="utf-8")
    r = scan_contest_package_file(
        f, "level_demo", 1, contest, {}, forbid_relative_in_logic=False
    )
    assert not any(v.kind == "RELATIVE_IN_LOGIC" for v in r.violations)


def test_contest_upward(tmp_path: Path) -> None:
    contest = tmp_path / "contests" / "level_demo"
    lev1 = contest / "level_1"
    f = lev1 / "a.py"
    f.parent.mkdir(parents=True)
    f.write_text(
        "from layers.layer_1_competition.level_1_impl.level_demo.level_2 import x\n",
        encoding="utf-8",
    )
    r = scan_contest_package_file(f, "level_demo", 1, contest, {})
    assert any(v.kind == "CONTEST_UPWARD" for v in r.violations)


def test_contest_deep_path_heuristic(tmp_path: Path) -> None:
    contest = tmp_path / "contests" / "level_demo"
    lev0 = contest / "level_0"
    lev0.mkdir(parents=True)
    (lev0 / "__init__.py").write_text(
        "from .submod import exported\n__all__ = ('exported',)\n",
        encoding="utf-8",
    )
    (lev0 / "submod.py").write_text("exported = 1\n", encoding="utf-8")
    lev1 = contest / "level_1"
    lev1.mkdir(parents=True)
    f = lev1 / "a.py"
    f.write_text(
        "from layers.layer_1_competition.level_1_impl.level_demo.level_0.submod "
        "import exported\n",
        encoding="utf-8",
    )
    r = scan_contest_package_file(f, "level_demo", 1, contest, {})
    assert any(v.kind == "CONTEST_DEEP_PATH" for v in r.violations)


def test_contest_root_relaxes_layering(tmp_path: Path) -> None:
    contest = tmp_path / "contests" / "level_demo"
    contest.mkdir(parents=True)
    f = contest / "hook.py"
    f.write_text(
        "from layers.layer_1_competition.level_1_impl.level_demo.level_1 import x\n",
        encoding="utf-8",
    )
    reports = scan_contest_root_directory(contest, "level_demo")
    assert len(reports) == 1
    r = reports[0]
    assert not any(v.kind == "CONTEST_UPWARD" for v in r.violations)
    assert not any(v.kind == "CONTEST_DEEP_PATH" for v in r.violations)


def test_special_tree_relative_in_logic(tmp_path: Path) -> None:
    root = tmp_path / "layer_Z_unsorted"
    f = root / "m.py"
    f.parent.mkdir(parents=True)
    f.write_text("from .x import y\n", encoding="utf-8")
    r = scan_special_tree_file(f)
    assert any(v.kind == "RELATIVE_IN_LOGIC" for v in r.violations)
