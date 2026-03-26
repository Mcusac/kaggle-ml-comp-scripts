"""Guard __init__.py export aggregation against list/tuple concat hazards."""

from __future__ import annotations

from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.validation.init_all_concat import (
    collect_init_all_concat_violations,
    find_scripts_root,
)


def test_init_all_concat_uses_list_safe_parts() -> None:
    """For aggregation __all__ chains, require list(child.__all__) and ban tuple literals."""
    scripts_root = find_scripts_root(Path(__file__))
    violations = collect_init_all_concat_violations(scripts_root)
    assert not violations, "Unsafe __all__ concat patterns found:\n" + "\n".join(violations)
