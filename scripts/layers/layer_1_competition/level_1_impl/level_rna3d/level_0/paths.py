"""Stanford RNA 3D Folding Part 2 path constants."""

from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


class RNA3DPaths(ContestPaths):
    """Paths for `stanford-rna-3d-folding-2` competition data."""

    @property
    def kaggle_dataset_name(self) -> str:
        """
        Kaggle input dataset name.

        For Kaggle code competitions, the competition data is typically mounted as:
          /kaggle/input/<competition-slug>
        """
        return "stanford-rna-3d-folding-2"

    @property
    def kaggle_competition_name(self) -> Optional[str]:
        """Kaggle competition slug."""
        return "stanford-rna-3d-folding-2"

    @property
    def local_data_path(self) -> str:
        """
        Default local data path.

        This mirrors the common local mimic layout:
          <repo>/input/stanford-rna-3d-folding-2/
        """
        return "../stanford-rna-3d-folding-2"
