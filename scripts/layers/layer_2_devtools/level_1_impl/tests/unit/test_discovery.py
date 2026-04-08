"""Tests for layered discovery operations (Step 1e queue)."""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[5]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from layers.layer_2_devtools.level_1_impl.level_0.targets.discovery_ops import (
    build_comprehensive_queue,
    default_layers_root,
)


def test_default_layers_root_points_at_scripts_layers() -> None:
    lr = default_layers_root(_SCRIPTS)
    assert lr.name == "layers"
    assert (lr / "layer_0_core").is_dir()


def test_comprehensive_queue_counts_and_precheck_kinds(tmp_path: Path) -> None:
    layers = tmp_path / "layers"
    core = layers / "layer_0_core"
    for n in (0, 1):
        (core / f"level_{n}").mkdir(parents=True)
    infra = layers / "layer_1_competition" / "level_0_infra"
    (infra / "level_0").mkdir(parents=True)
    impl = layers / "layer_1_competition" / "level_1_impl"
    zed = impl / "level_zebra"
    (zed / "level_0").mkdir(parents=True)
    (zed / "root_mod.py").write_text("# stub\n", encoding="utf-8")
    alpha = impl / "level_alpha"
    (alpha / "level_0").mkdir(parents=True)
    (layers / "layer_Z_unsorted" / "pkg").mkdir(parents=True)

    q = build_comprehensive_queue(layers)
    assert len(q) == 7

    kinds = [t.precheck_kind for t in q]
    assert kinds.count("general_level") == 2
    assert kinds.count("infra") == 1
    assert kinds.count("contest_tier") == 2
    assert kinds.count("contest_root") == 1
    assert kinds.count("special_tree") == 1

    assert q[0].level_name == "level_0" and q[0].audit_scope == "general"
    zebra_tier = next(t for t in q if t.level_name == "level_zebra_level_0")
    assert zebra_tier.segment_id == "contests_special:level_zebra"
    zebra_root = next(t for t in q if t.level_name == "level_zebra_root")
    assert zebra_root.precheck_kind == "contest_root"
    alpha_before_zebra = q.index(next(t for t in q if t.level_name == "level_alpha_level_0"))
    zebra_start = q.index(zebra_tier)
    assert alpha_before_zebra < zebra_start

    z = next(t for t in q if t.level_name == "layer_Z_unsorted")
    assert z.precheck_kind == "special_tree"


def test_segment_index_increments_per_segment(tmp_path: Path) -> None:
    layers = tmp_path / "layers"
    (layers / "layer_0_core" / "level_0").mkdir(parents=True)
    (layers / "layer_1_competition" / "level_0_infra" / "level_0").mkdir(parents=True)

    q = build_comprehensive_queue(layers)
    assert q[0].segment_index == 0
    assert q[1].segment_index == 1
