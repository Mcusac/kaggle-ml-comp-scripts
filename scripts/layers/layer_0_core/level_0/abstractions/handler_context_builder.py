"""Protocol for building handler context without orchestration importing contest."""

from typing import Any, Protocol, Tuple
import argparse


class HandlerContextBuilder(Protocol):
    """
    Builds context for framework command handlers.
    Implemented by the scripts/contest layer; orchestration uses this via dependency injection.
    """

    def detect_contest(self, args: argparse.Namespace) -> str:
        """Return contest name from args or environment."""
        ...

    def get_config(self, contest_name: str, args: argparse.Namespace) -> Any:
        """Return configuration object for the contest."""
        ...

    def get_paths(self, contest_name: str) -> Any:
        """Return paths object for the contest."""
        ...

    def get_data_schema(self, contest_name: str) -> Any:
        """Return data schema for the contest, or None."""
        ...

    def load_contest_data(
        self,
        contest_name: str,
        model_type: str,
        **kwargs: Any,
    ) -> Tuple[Any, Any, Any]:
        """Load train, validation, and test data. Returns (train_data, val_data, test_data)."""
        ...
