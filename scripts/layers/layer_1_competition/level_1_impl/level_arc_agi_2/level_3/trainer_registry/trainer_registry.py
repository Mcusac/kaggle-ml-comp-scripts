"""Register ARC trainable models (neural + future): RNA3D-style ``(data_root, output_dir)`` trainers."""

from typing import Callable, Optional

from layers.layer_0_core.level_0 import get_logger, NamedRegistry

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import run_grid_cnn_training

_logger = get_logger(__name__)

TrainerFn = Callable[[str, str], None]
REGISTRY = NamedRegistry[TrainerFn](registry_name="ARCTrainerRegistry", key_label="Model")


def _train_grid_cnn_v0(data_root: str, output_dir: str) -> None:
    run_grid_cnn_training(data_root, output_dir)

REGISTRY.set("grid_cnn_v0", _train_grid_cnn_v0)


def get_trainer(model_name: str) -> Optional[TrainerFn]:
    return REGISTRY.get(model_name)


def list_available_models() -> list[str]:
    return REGISTRY.list_keys()
