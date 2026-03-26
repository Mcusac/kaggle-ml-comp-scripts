"""ARC-AGI-2 schema surface for framework compatibility."""

from layers.layer_1_competition.level_0_infra.level_0 import ContestDataSchema


class ARC26DataSchema(ContestDataSchema):
    """ARC data is JSON task-based and does not expose tabular target columns."""

    @property
    def sample_id_column(self) -> str:
        return "task_id"

    @property
    def target_columns(self) -> list[str]:
        return []

    def validate_sample_id(self, sample_id: str) -> bool:
        return bool(str(sample_id).strip())

