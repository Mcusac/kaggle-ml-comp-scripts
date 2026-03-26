from pathlib import Path

import pytest

pytest.importorskip("contest")


def test_csiro_paths_contract_methods_exist_and_return_paths() -> None:
    """
    Ensure contest paths implement the runtime contract used by CSIRO pipelines.

    This is a lightweight guardrail to catch missing-method regressions like:
    AttributeError: 'CSIROPaths' object has no attribute 'get_output_dir'
    """
    import contest.implementations  # noqa: F401
    from contest.registry import get_contest

    contest = get_contest("csiro")
    paths = contest["paths"]()

    assert callable(getattr(paths, "get_output_dir", None))
    assert callable(getattr(paths, "get_data_root", None))
    assert callable(getattr(paths, "get_models_base_dir", None))

    assert isinstance(paths.get_output_dir(), Path)
    assert isinstance(paths.get_data_root(), Path)
    assert isinstance(paths.get_models_base_dir(), Path)
