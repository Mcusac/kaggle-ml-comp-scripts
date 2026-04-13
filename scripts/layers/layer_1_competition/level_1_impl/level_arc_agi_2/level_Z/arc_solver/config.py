"""
WorkerConfig — dataclass that captures every axis of variation between solver versions.

Each solver version (v1, v2, v3) constructs a WorkerConfig with its specific settings
and passes it to ``worker_core``.  Adding a new variant means adding a new config, not
touching any shared logic.
"""

from dataclasses import dataclass, field
from typing import Callable, Type

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()


# ---------------------------------------------------------------------------
# Batch-construction strategies
# ---------------------------------------------------------------------------

def build_batches_grouped(test_id_to_subkeys: dict) -> list:
    """
    v1 / v2 strategy: group subkeys in pairs of 4 across complementary rotation
    offsets so that each forward pass covers a diverse set of augmentations.

    Offset layout (per test_id):
      [0,4]  → permute × 2  +  rot90² permute × 2
      [2,6]  → rot90 permute × 2  +  rot90³ permute × 2
      [8,12] → transpose permute × 2  +  transpose rot90² permute × 2
      [10,14]→ transpose rot90 permute × 2  +  transpose rot90³ permute × 2
    """
    batches = []
    for subkeys in test_id_to_subkeys.values():
        for pair in ([0, 4], [2, 6]):
            batch = []
            for offset in pair:
                batch.extend(subkeys[offset : offset + 2])
            batches.append(batch)
    for subkeys in test_id_to_subkeys.values():
        for pair in ([8, 12], [10, 14]):
            batch = []
            for offset in pair:
                batch.extend(subkeys[offset : offset + 2])
            batches.append(batch)
    return batches


def build_batches_single(test_id_to_subkeys: dict) -> list:
    """
    v3 strategy: one subkey per batch — maximises memory headroom at the cost
    of lower parallelism.
    """
    batches = []
    for subkeys in test_id_to_subkeys.values():
        for subkey in subkeys:
            batches.append([subkey])
    return batches


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class WorkerConfig:
    """All per-version knobs, collected in one place."""

    # --- Model ---
    model_name: str
    max_seq_length: int
    model_load_kwargs: dict = field(default_factory=dict)

    # --- PEFT ---
    peft_params: dict = field(default_factory=dict)

    # --- Training ---
    train_args: dict = field(default_factory=dict)
    trainer_class: Type = None  # UnslothFixedTrainer or UnslothV3FixedTrainer

    # --- Attention patching ---
    # Callable with no arguments; called once at worker startup.
    install_attention: Callable[[], None] = None

    # --- Post-PEFT model setup ---
    # Optional callable: (model) -> model, run after get_peft_model.
    post_peft_setup: Callable = None

    # --- Post-training cleanup ---
    # Optional callable: (model, trainer) -> None, run inside the redirect block.
    post_train_cleanup: Callable = None

    # --- Batch construction ---
    build_batches: Callable[[dict], list] = field(default_factory=lambda: build_batches_grouped)

    # --- Inference output directory ---
    dir_outputs: str = "/kaggle/inference_outputs"

    # --- Post-batch memory cleanup ---
    # Optional callable: (tokens, dfs_result) -> None, run after each inference batch.
    post_batch_cleanup: Callable = None

    # --- Misc ---
    disable_amp_grad_scaler: bool = False
    extra_env_vars: dict = field(default_factory=dict)