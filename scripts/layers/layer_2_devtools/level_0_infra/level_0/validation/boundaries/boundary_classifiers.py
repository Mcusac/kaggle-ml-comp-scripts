"""Classify internal module names into boundary nodes.

This is deliberately string-based and conservative (no runtime importing).
"""

from __future__ import annotations

from dataclasses import dataclass

from .boundary_nodes import BoundaryNode


def _parse_int_suffix(part: str, prefix: str) -> int | None:
    if not part.startswith(prefix):
        return None
    rest = part[len(prefix) :]
    if rest.isdigit():
        return int(rest)
    return None


@dataclass(frozen=True)
class BoundaryClassifyResult:
    node: BoundaryNode | None
    node_kind: str
    level: int | None = None
    contest_slug: str | None = None


def classify_module_to_boundary(module: str) -> BoundaryClassifyResult:
    """Map module name -> BoundaryNode (or None if out of scope).

    Supported internal shapes:
    - General stack: ``level_N...`` and ``layers.layer_0_core.level_N...``
    - Competition infra: ``layers.layer_1_competition.level_0_infra.level_N...``
    - Contests: ``layers.layer_1_competition.level_1_impl.<slug>.level_K...``
    - Devtools: ``layers.layer_2_devtools.level_0_infra.level_M...`` / ``...level_1_impl.level_M...``
    - Optional legacy dev scripts: ``dev...``
    """
    parts = module.split(".")
    if not parts:
        return BoundaryClassifyResult(node=None, node_kind="unknown")

    # General stack (preferred runtime import style): level_N...
    if parts[0].startswith("level_"):
        n = _parse_int_suffix(parts[0], "level_")
        if n is not None:
            node = BoundaryNode(
                key=f"general_level_{n}",
                label=f"general level_{n}",
                sort_key=("general", n),
            )
            return BoundaryClassifyResult(node=node, node_kind="general", level=n)

    # General stack (explicit core namespace): layers.layer_0_core.level_N...
    if parts[:2] == ["layers", "layer_0_core"] and len(parts) >= 3:
        n = _parse_int_suffix(parts[2], "level_")
        if n is not None:
            node = BoundaryNode(
                key=f"general_level_{n}",
                label=f"general level_{n}",
                sort_key=("general", n),
            )
            return BoundaryClassifyResult(node=node, node_kind="general", level=n)

    # Competition infra: layers.layer_1_competition.level_0_infra.level_N...
    if parts[:3] == ["layers", "layer_1_competition", "level_0_infra"] and len(parts) >= 4:
        n = _parse_int_suffix(parts[3], "level_")
        if n is not None:
            node = BoundaryNode(
                key=f"competition_infra_level_{n}",
                label=f"competition infra level_{n}",
                sort_key=("competition_infra", n),
            )
            return BoundaryClassifyResult(node=node, node_kind="competition_infra", level=n)

    # Contests: layers.layer_1_competition.level_1_impl.<slug>.level_K...
    if parts[:3] == ["layers", "layer_1_competition", "level_1_impl"] and len(parts) >= 5:
        slug = parts[3]
        k = _parse_int_suffix(parts[4], "level_")
        if k is not None:
            node = BoundaryNode(
                key=f"contest_{slug}_level_{k}",
                label=f"contest {slug} level_{k}",
                sort_key=("contest", slug, k),
            )
            return BoundaryClassifyResult(
                node=node, node_kind="contest", level=k, contest_slug=slug
            )

    # Devtools: layers.layer_2_devtools.level_0_infra.level_M... / level_1_impl.level_M...
    if parts[:2] == ["layers", "layer_2_devtools"] and len(parts) >= 4:
        if parts[2] == "level_0_infra" and parts[3].startswith("level_"):
            m = _parse_int_suffix(parts[3], "level_")
            if m is not None:
                node = BoundaryNode(
                    key=f"devtools_infra_level_{m}",
                    label=f"devtools infra level_{m}",
                    sort_key=("devtools_infra", m),
                )
                return BoundaryClassifyResult(node=node, node_kind="devtools_infra", level=m)
        if parts[2] == "level_1_impl" and parts[3].startswith("level_"):
            m = _parse_int_suffix(parts[3], "level_")
            if m is not None:
                node = BoundaryNode(
                    key=f"devtools_impl_level_{m}",
                    label=f"devtools impl level_{m}",
                    sort_key=("devtools_impl", m),
                )
                return BoundaryClassifyResult(node=node, node_kind="devtools_impl", level=m)

    # Optional legacy dev scripts
    if parts[0] == "dev":
        node = BoundaryNode(key="dev_scripts", label="dev scripts", sort_key=("dev_scripts",))
        return BoundaryClassifyResult(node=node, node_kind="dev_scripts")

    return BoundaryClassifyResult(node=None, node_kind="external_or_unknown")

