"""Load checkpoint and predict output grid for a test input (v0 trim-to-input-size)."""

from pathlib import Path

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_4 import load_json_raw

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import CANVAS_SIZE, grid_to_one_hot_tensor, logits_to_grid
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import TinyGridCNN

logger = get_logger(__name__)


def predict_grid_from_checkpoint(
    input_grid: list[list[int]],
    checkpoint_path: str | Path,
    train_config_path: str | Path,
) -> list[list[int]]:
    """Forward pass; output cropped to input height/width (see v0 limitation if target differs)."""
    torch = get_torch()
    if torch is None:
        raise RuntimeError("PyTorch is required for neural ARC inference.")

    ckpt = Path(checkpoint_path)
    cfg_p = Path(train_config_path)
    if not ckpt.is_file():
        raise FileNotFoundError(f"Missing checkpoint: {ckpt}")
    if not cfg_p.is_file():
        raise FileNotFoundError(f"Missing train config: {cfg_p}")
    cfg = load_json_raw(cfg_p)
    canvas = int(cfg.get("canvas_size", CANVAS_SIZE))
    num_classes = int(cfg.get("num_classes", 10))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TinyGridCNN(num_classes=num_classes).to(device)
    state = torch.load(ckpt, map_location=device)
    model.load_state_dict(state)
    model.eval()

    oh = grid_to_one_hot_tensor(input_grid, canvas=canvas).unsqueeze(0).to(device)
    orig_h, orig_w = len(input_grid), len(input_grid[0]) if input_grid else (0, 0)
    with torch.no_grad():
        logits = model(oh)[0]
    return logits_to_grid(logits.cpu(), orig_h, orig_w)
