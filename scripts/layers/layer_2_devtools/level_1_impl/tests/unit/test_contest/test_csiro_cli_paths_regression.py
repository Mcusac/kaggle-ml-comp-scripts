import argparse
import sys
import types
from unittest.mock import patch

import pytest

pytest.importorskip("contest")


def test_csiro_cleanup_grid_search_handler_does_not_crash_on_paths_contract() -> None:
    """
    Regression test: CSIRO cleanup handler previously crashed because CSIROPaths
    lacked get_output_dir(). This calls the handler with side effects mocked out.
    """
    import contest.implementations  # noqa: F401

    # Importing the CSIRO CLI pulls in utils.system.device (torch). On Windows,
    # torch can be installed but unusable (DLL load failures). For this test we
    # only need the CLI handler + paths contract, so we stub torch at import time.
    if "torch" not in sys.modules:
        torch_stub = types.ModuleType("torch")

        class _DummyDevice:
            def __init__(self, spec: str):
                self.type = "cuda" if str(spec).startswith("cuda") else "cpu"

        def _device(spec: str) -> _DummyDevice:
            return _DummyDevice(spec)

        torch_stub.device = _device  # type: ignore[attr-defined]
        torch_stub.nn = types.SimpleNamespace(Module=object)  # type: ignore[attr-defined]
        torch_stub.cuda = types.SimpleNamespace(  # type: ignore[attr-defined]
            is_available=lambda: False,
            device_count=lambda: 0,
            get_device_name=lambda *_args, **_kwargs: "CPU",
        )
        sys.modules["torch"] = torch_stub

    from contest.implementations.csiro import cli as csiro_cli

    args = argparse.Namespace(
        model_dir=None,
        results_file=None,
        keep_top=1,
    )

    with patch(
        "contest.implementations.csiro.modeling.utils.cleanup.cleanup_grid_search_checkpoints_retroactive",
        return_value=(0, 0),
    ):
        csiro_cli._handle_cleanup_grid_search(args)
