"""Notebook environment bootstrap: delegates to ``path_bootstrap`` (scripts-root)."""

from typing import Optional

from path_bootstrap import bootstrap_notebook_environment as _bootstrap_notebook_environment


def bootstrap_notebook(
    *,
    contest: Optional[str] = None,
    scripts_package: str = "kaggle-ml-comp-scripts",
) -> str:
    """Prepare ``sys.path`` for competition notebooks.

    Requires ``scripts`` to be importable (e.g. notebook already ran
    ``sys.path.insert(0, resolve_notebook_scripts_path(...))`` before importing
    from ``layers``). Prefer calling :func:`path_bootstrap.bootstrap_notebook_environment`
    from the notebook first cell after that insert.

    Returns:
        ``scripts_path`` string (for logging).
    """
    return _bootstrap_notebook_environment(contest=contest, scripts_package=scripts_package)
