"""Contest path utilities: Kaggle input detection and data root resolution."""

from typing import Optional

from layers.layer_0_core.level_0 import is_kaggle_input

from ..contest.paths import ContestPaths


def resolve_data_root(
    data_root: Optional[str],
    paths: ContestPaths,
) -> str:
    """
    Resolve data root from an explicit string or a ContestPaths instance.

    Use this when you already have a ``ContestPaths`` object (e.g. from the
    contest registry). For CLI flows that only have ``argparse.Namespace``,
    use ``resolve_data_root_from_args`` in ``infra.level_1.contest.cli`` instead.
    """
    if data_root is not None and data_root.strip():
        return data_root.strip()
    return str(paths.get_data_root())


__all__ = ["is_kaggle_input", "resolve_data_root"]
