"""Stanford RNA 3D Folding Part 2 data schema helpers."""

from dataclasses import dataclass
from typing import List

from layers.layer_1_competition.level_0_infra.level_0 import ContestDataSchema


def build_coordinate_columns(n_structures: int = 5) -> List[str]:
    """
    Build coordinate column names for Kaggle submission.

    The competition expects x/y/z for each of 5 predicted structures:
      x_1,y_1,z_1,...,x_5,y_5,z_5
    """
    cols: List[str] = []
    for k in range(1, n_structures + 1):
        cols.extend([f"x_{k}", f"y_{k}", f"z_{k}"])
    return cols


@dataclass(frozen=True)
class RNA3DDataSchema(ContestDataSchema):
    """Schema for RNA 3D Folding Part 2 competition CSVs."""

    n_structures: int = 5

    @property
    def sample_id_column(self) -> str:
        """Sequence identifier column in *sequences.csv files."""
        return "target_id"

    @property
    def target_columns(self) -> List[str]:
        """Submission coordinate columns."""
        return build_coordinate_columns(self.n_structures)

    def validate_sample_id(self, sample_id: str) -> bool:
        """Valid IDs are non-empty strings."""
        return isinstance(sample_id, str) and len(sample_id.strip()) > 0
