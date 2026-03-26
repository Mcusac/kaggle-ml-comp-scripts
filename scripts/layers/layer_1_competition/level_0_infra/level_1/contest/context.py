"""Contest context builder for pipelines."""

from dataclasses import dataclass
from typing import Any

from ..registry import get_contest


@dataclass
class ContestContext:
    """
    Resolved contest context for pipeline execution.

    Holds instances of paths, config, data_schema, and post_processor.
    Provides get_* methods for pipelines that expect a context protocol.
    """

    paths: Any
    config: Any
    data_schema: Any
    post_processor: Any

    @property
    def local_data_root(self) -> str:
        """Convenience: data root path as string."""
        return str(self.paths.local_data_root)

    def get_paths(self) -> Any:
        """Return paths instance (for pipelines expecting get_* API)."""
        return self.paths

    def get_config(self) -> Any:
        """Return config instance (for pipelines expecting get_* API)."""
        return self.config

    def get_data_schema(self) -> Any:
        """Return data_schema instance (for pipelines expecting get_* API)."""
        return self.data_schema

    def get_post_processor(self) -> Any:
        """Return post_processor instance (for pipelines expecting get_* API)."""
        return self.post_processor


def build_contest_context(contest_name: str) -> ContestContext:
    """
    Build contest context from registry.

    Args:
        contest_name: Registered contest name (e.g., 'csiro', 'cafa')

    Returns:
        ContestContext with paths, config, data_schema, post_processor instances
    """
    contest = get_contest(contest_name)
    paths = contest["paths"]()
    config = contest["config"]()
    data_schema = contest["data_schema"]()
    post_processor = contest["post_processor"]()
    return ContestContext(
        paths=paths,
        config=config,
        data_schema=data_schema,
        post_processor=post_processor,
    )
