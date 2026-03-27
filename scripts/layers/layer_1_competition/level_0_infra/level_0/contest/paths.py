"""Contest paths abstract base class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_0 import is_kaggle


def _find_mimic_data_root(kaggle_dataset_name: str, from_file: str) -> Optional[Path]:
    """
    Find data root in local mimic layout (input/ = /kaggle/input, working/ = /kaggle/working).
    Walks up from from_file until a directory contains "input/", then returns
    project_root / "input" / kaggle_dataset_name.
    """
    try:
        for p in Path(from_file).resolve().parents:
            if (p / "input").is_dir():
                return p / "input" / kaggle_dataset_name
    except Exception:
        pass
    return None


class ContestPaths(ABC):
    """
    Abstract base class for contest-specific path constants.

    Defines paths for Kaggle datasets and local development.
    """

    @property
    @abstractmethod
    def kaggle_dataset_name(self) -> str:
        """
        Return Kaggle dataset name.

        Example: 'csiro-biomass' or 'cafa-6-protein'

        Returns:
            Kaggle dataset name
        """
        ...

    @property
    @abstractmethod
    def kaggle_competition_name(self) -> Optional[str]:
        """
        Return Kaggle competition name, if applicable.

        Returns:
            Kaggle competition name, or None if not a competition
        """
        ...

    @property
    @abstractmethod
    def local_data_path(self) -> str:
        """
        Return local data path for development.

        Returns:
            Local path to data directory
        """
        ...

    @property
    def kaggle_input_path(self) -> str:
        """
        Return Kaggle input path.

        Returns:
            Path to Kaggle input directory
        """
        return f"/kaggle/input/{self.kaggle_dataset_name}"

    @property
    def kaggle_working_path(self) -> str:
        """
        Return Kaggle working directory path.

        Returns:
            Path to Kaggle working directory
        """
        return "/kaggle/working"

    @property
    def local_data_root(self) -> Path:
        """
        Data root for this contest: Kaggle input, local mimic (input/), or local_data_path.

        - On Kaggle: /kaggle/input/<kaggle_dataset_name>
        - On Kaggle (competition mount): /kaggle/input/competitions/<kaggle_competition_name>
        - Local mimic (repo with input/): <project_root>/input/<kaggle_dataset_name>
        - Else: Path(local_data_path) resolved against cwd
        """
        if is_kaggle():
            comp_name = (self.kaggle_competition_name or "").strip()
            if comp_name:
                comp_root = Path("/kaggle/input/competitions") / comp_name
                if comp_root.exists():
                    return comp_root
            return Path(self.kaggle_input_path)
        mimic = _find_mimic_data_root(self.kaggle_dataset_name, __file__)
        if mimic is not None:
            return mimic
        return Path(self.local_data_path).resolve()

    def get_data_root(self) -> Path:
        """
        Return the data root as a Path.

        This method exists as a stable runtime contract for pipelines that expect a
        `get_data_root()` method on contest paths implementations.
        """
        return self.local_data_root

    def get_output_dir(self) -> Path:
        """
        Return the output root directory as a Path.

        - On Kaggle: /kaggle/working
        - Locally: output/
        """
        if is_kaggle():
            return Path(self.kaggle_working_path)
        return Path("output")

    def get_models_base_dir(self) -> Path:
        """
        Base directory for stored/exported models.

        Default matches the training/export output root. Contests with a separate
        models input dataset (e.g. CSIRO) should override.
        """
        return self.get_output_dir()
