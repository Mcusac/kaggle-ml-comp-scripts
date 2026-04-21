"""Training-row construction + collator token ID resolution for per-task LoRA adaptation."""

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    apply_augmentation,
    coerce_arc_grid,
    generate_augmentation_specs,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    train_trim_task_train_pairs_to_token_budget,
)


def resolve_collator_token_ids(tokenizer, formatter):
    eos_ids = tokenizer.encode(str(formatter.im_end), add_special_tokens=False)
    if len(eos_ids) != 1:
        raise ValueError("im_end must encode to one token")

    eos_id = int(eos_ids[0])

    u = tokenizer.encode(formatter.im_user, add_special_tokens=False)
    a = tokenizer.encode(formatter.im_assistant, add_special_tokens=False)

    if int(u[0]) == int(a[0]):
        user_tid, assistant_tid = int(u[1]), int(a[1])
    else:
        user_tid, assistant_tid = int(u[0]), int(a[0])

    return user_tid, assistant_tid, eos_id


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
