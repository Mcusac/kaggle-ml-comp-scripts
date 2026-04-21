"""Training-row construction for per-task LoRA adaptation."""

from layers.layer_1_competition.level_0_infra.level_0 import resolve_collator_token_ids

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    apply_augmentation,
    coerce_arc_grid,
    generate_augmentation_specs,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    train_trim_task_train_pairs_to_token_budget,
)


def build_task_training_rows(
    task_payload,
    formatter,
    *,
    n_augmentations,
    augment_seed,
    max_seq_length,
):
    train = task_payload.get("train")
    if not train:
        return []

    base_pairs = []
    for x in train:
        if isinstance(x, dict):
            base_pairs.append(
                {
                    "input": coerce_arc_grid(x["input"], x["input"]),
                    "output": coerce_arc_grid(x["output"], x["output"]),
                }
            )

    specs = generate_augmentation_specs(
        max(1, int(n_augmentations)),
        seed=int(augment_seed),
        include_identity=True,
    )

    rows = []

    for spec in specs:
        aug = [
            {
                "input": apply_augmentation(p["input"], spec),
                "output": apply_augmentation(p["output"], spec),
            }
            for p in base_pairs
        ]

        trimmed = train_trim_task_train_pairs_to_token_budget(
            {"train": aug},
            formatter,
            max_len=int(max_seq_length),
        )

        if not trimmed.get("train"):
            continue

        text = formatter.fmt_train_block(
            trimmed["train"],
            last_is_challenge=False,
        )

        rows.append({"text": text})

    return rows