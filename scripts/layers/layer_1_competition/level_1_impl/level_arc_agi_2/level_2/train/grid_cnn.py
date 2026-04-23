"""Train TinyGridCNN and persist checkpoint + train_config.json."""

from pathlib import Path

from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch
from layers.layer_0_core.level_1 import train_one_epoch
from layers.layer_0_core.level_4 import save_json

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    CANVAS_SIZE,
    NUM_CHANNELS,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcSameShapeGridDataset,
    collect_same_shape_train_pairs,
    TinyGridCNN,
)

_logger = get_logger(__name__)

DEFAULT_EPOCHS = 5
DEFAULT_BATCH = 8
DEFAULT_LR = 1e-3


def run_grid_cnn_training(data_root: str, output_dir: str, *, epochs: int | None = None) -> None:
    """Fit ``TinyGridCNN``.on same-shape training pairs; write ``model.pt`` and ``train_config.json``."""
    torch = get_torch()
    if torch is None:
        raise RuntimeError("PyTorch is required for grid_cnn_v0 training (install torch).")

    pairs = collect_same_shape_train_pairs(data_root)
    if not pairs:
        raise ValueError("No same-shape (input/output) train pairs found; cannot train grid_cnn_v0.")

    out = Path(output_dir)
    ensure_dir(out)
    n_epochs = int(epochs if epochs is not None else DEFAULT_EPOCHS)

    ds = ArcSameShapeGridDataset(pairs, canvas=CANVAS_SIZE)
    loader = torch.utils.data.DataLoader(
        ds,
        batch_size=min(DEFAULT_BATCH, len(ds)),
        shuffle=True,
        num_workers=0,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TinyGridCNN(num_classes=NUM_CHANNELS).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=DEFAULT_LR)
    loss_fn = torch.nn.CrossEntropyLoss()

    config = {
        "model_key": "grid_cnn_v0",
        "canvas_size": CANVAS_SIZE,
        "num_classes": NUM_CHANNELS,
        "epochs": n_epochs,
        "batch_size": min(DEFAULT_BATCH, len(ds)),
        "lr": DEFAULT_LR,
        "schema_version": 1,
        "num_train_pairs": len(pairs),
    }
    cfg_path = out / "train_config.json"
    save_json(config, cfg_path, indent=2, ensure_ascii=True)

    def batch_processor(batch: tuple) -> torch.Tensor:
        xb, yb, _meta = batch
        xb = xb.to(device)
        yb = yb.to(device)
        logits = model(xb)
        loss = loss_fn(logits, yb)
        return loss

    model.train()
    for ep in range(n_epochs):
        avg = train_one_epoch(loader, batch_processor=batch_processor, optimizer=opt, scaler=None)
        _logger.info("Epoch %d/%d train loss=%.4f", ep + 1, n_epochs, avg)

    ckpt = out / "model.pt"
    torch.save(model.state_dict(), ckpt)
    _logger.info("Saved ARC grid CNN weights: %s", ckpt)
