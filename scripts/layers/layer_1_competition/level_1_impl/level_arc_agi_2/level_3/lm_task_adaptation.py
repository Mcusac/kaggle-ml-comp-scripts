"""Per-task Unsloth LoRA adaptation (NVARC reference worker training loop).

Builds a small ``datasets.Dataset`` from task ``train`` pairs + geometric augmentations,
uses ``QwenDataCollatorForCompletionOnlyLM``-style completion masking, then
``UnslothFixedTrainer`` + ``UnslothTrainingArguments`` matching the reference notebook
(reset adapter → ``for_training`` → ``train`` → unwrap → ``for_inference``).
"""

import gc
import importlib
import io
import tempfile
import numpy as np

from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Union

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    apply_augmentation,
    coerce_arc_grid,
    generate_augmentation_specs,
    ArcLmAdaptationConfig,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import ArcQwenGridChatFormatter
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    train_trim_task_train_pairs_to_token_budget,
)

logger = get_logger(__name__)

Grid = list[list[int]]

_DataCollatorForLanguageModeling = getattr(importlib.import_module("transformers"), "DataCollatorForLanguageModeling")


def _resolve_collator_token_ids(tokenizer: Any, formatter: ArcQwenGridChatFormatter) -> tuple[int, int, int]:
    """Infer user / assistant / EOS single-token ids for completion masking (Qwen chat)."""
    eos_ids = tokenizer.encode(str(formatter.im_end), add_special_tokens=False)
    if not isinstance(eos_ids, list) or len(eos_ids) != 1:
        raise ValueError(f"im_end must encode to exactly one token; got {eos_ids!r}")
    eos_id = int(eos_ids[0])
    u = tokenizer.encode(formatter.im_user, add_special_tokens=False)
    a = tokenizer.encode(formatter.im_assistant, add_special_tokens=False)
    if not isinstance(u, list) or not isinstance(a, list) or len(u) < 2 or len(a) < 2:
        raise ValueError(f"Cannot infer chat markers from im_user/im_assistant encodings: {u!r} {a!r}")
    if int(u[0]) == int(a[0]):
        user_tid, assistant_tid = int(u[1]), int(a[1])
    else:
        user_tid, assistant_tid = int(u[0]), int(a[0])
    return user_tid, assistant_tid, eos_id


def build_task_training_rows(
    task_payload: dict[str, Any],
    formatter: ArcQwenGridChatFormatter,
    *,
    n_augmentations: int,
    augment_seed: int,
    max_seq_length: int,
) -> list[dict[str, str]]:
    """Rows with ``text`` key (NVARC ``Dataset.from_list`` layout), one per augmentation draw."""
    train = task_payload.get("train")
    if not isinstance(train, list) or not train:
        return []
    base_pairs: list[dict[str, Grid]] = []
    for x in train:
        if not isinstance(x, dict):
            continue
        gi = x.get("input")
        go = x.get("output")
        if isinstance(gi, list) and isinstance(go, list):
            gi2 = coerce_arc_grid(gi, gi)
            go2 = coerce_arc_grid(go, go)
            base_pairs.append({"input": gi2, "output": go2})
    if not base_pairs:
        return []
    n = max(1, int(n_augmentations))
    specs = generate_augmentation_specs(n, seed=int(augment_seed), include_identity=True)[:n]
    rows: list[dict[str, str]] = []
    for spec in specs:
        aug_train: list[dict[str, Any]] = []
        for p in base_pairs:
            aug_train.append(
                {
                    "input": apply_augmentation(p["input"], spec),
                    "output": apply_augmentation(p["output"], spec),
                }
            )
        trimmed = train_trim_task_train_pairs_to_token_budget(
            {"train": aug_train},
            formatter,
            max_len=int(max_seq_length),
        )
        tlist: list[dict[str, Grid]] = []
        for item in trimmed.get("train") or []:
            if not isinstance(item, dict):
                continue
            ii, oo = item.get("input"), item.get("output")
            if isinstance(ii, list) and isinstance(oo, list):
                tlist.append({"input": ii, "output": oo})
        if not tlist:
            continue
        text = formatter.fmt_train_block(tlist, last_is_challenge=False)
        rows.append({"text": text})
    return rows


class QwenDataCollatorForCompletionOnlyLM(_DataCollatorForLanguageModeling):
    """Notebook ``QwenDataCollatorForCompletionOnlyLM`` (HF MLM collator + Qwen chat masking)."""

    def __init__(
        self,
        tokenizer: Any,
        *,
        mlm: bool = False,
        user_id: int,
        assistant_id: int,
        eos_id: int,
    ) -> None:
        super().__init__(tokenizer=tokenizer, mlm=mlm)
        self.user_id = int(user_id)
        self.assistant_id = int(assistant_id)
        self.eos_id = int(eos_id)

    def torch_call(self, examples: list[Union[list[int], Any, dict[str, Any]]]) -> dict[str, Any]:
        batch = super().torch_call(examples)
        for i in range(len(examples)):
            labels = batch["input_ids"][i].clone()
            user_start_idx = np.where(labels.cpu().numpy() == self.user_id)[0].tolist()
            assistant_start_idx = np.where(labels.cpu().numpy() == self.assistant_id)[0].tolist()
            start_idx = sorted(user_start_idx + assistant_start_idx)
            end_idx = np.where(labels.cpu().numpy() == self.eos_id)[0]
            batch["labels"][i, :] = -100
            for j, (start, end) in enumerate(zip(start_idx, end_idx)):
                if int(start) >= int(end):
                    continue
                if j % 2 == 1:
                    start2 = int(start) + 2
                    end2 = int(end) + 1
                    if start2 < end2:
                        batch["labels"][i, start2:end2] = labels[start2:end2]
        return batch


_unsloth_fixed_trainer_cls: type | None = None


def _unsloth_fixed_trainer_class() -> type:
    """Build subclass so ``compute_loss`` is actually used (NVARC Unsloth issue #2435)."""

    global _unsloth_fixed_trainer_cls
    if _unsloth_fixed_trainer_cls is not None:
        return _unsloth_fixed_trainer_cls

    unsloth = importlib.import_module("unsloth")
    UnslothTrainer = getattr(unsloth, "UnslothTrainer")

    class UnslothFixedTrainer(UnslothTrainer):
        def compute_loss(self, model: Any, inputs: dict[str, Any], return_outputs: bool = False, **kwargs: Any):
            if getattr(self, "label_smoother", None) is not None and "labels" in inputs:
                labels = inputs.pop("labels")
            else:
                labels = None
            outputs = model(**inputs)
            if labels is not None:
                unwrapped_model = self.accelerator.unwrap_model(model)
                name_fn = getattr(unwrapped_model, "_get_name", None)
                name_l = str(name_fn()).lower() if callable(name_fn) else str(unwrapped_model.__class__.__name__).lower()
                if "unsloth" in name_l:
                    loss = self.label_smoother(outputs, labels, shift_labels=True)
                else:
                    loss = self.label_smoother(outputs, labels)
            else:
                loss = outputs["loss"] if isinstance(outputs, dict) else outputs[0]
            if hasattr(loss, "clone"):
                loss = loss.clone()
            if self.accelerator.num_processes > 1:
                loss = loss * self.accelerator.num_processes
            return (loss, outputs) if return_outputs else loss

    _unsloth_fixed_trainer_cls = UnslothFixedTrainer
    return UnslothFixedTrainer


def run_unsloth_task_adaptation(
    *,
    model: Any,
    tokenizer: Any,
    default_adapter_state: dict[str, Any],
    task_payload: dict[str, Any],
    budget_expired: callable,
    adaptation: ArcLmAdaptationConfig,
    max_seq_length: int,
) -> tuple[dict[str, Any], Any]:
    """One NVARC-style adapter reset + ``trainer.train()`` on per-task rows.

    Returns ``(meta, model)`` so the backend can keep the post-``for_inference`` module reference.
    """
    if budget_expired():
        return (
            {"status": "skipped_budget", "backend": "unsloth", "reason": "budget_expired_before_train"},
            model,
        )

    torch = importlib.import_module("torch")
    unsloth = importlib.import_module("unsloth")
    peft = importlib.import_module("peft")
    datasets = importlib.import_module("datasets")
    FastLanguageModel = getattr(unsloth, "FastLanguageModel")
    UnslothTrainingArguments = getattr(unsloth, "UnslothTrainingArguments")
    set_peft_model_state_dict = getattr(peft, "set_peft_model_state_dict")

    formatter = ArcQwenGridChatFormatter(tokenizer=tokenizer)
    device = next(model.parameters()).device
    restore = {k: v.to(device) if hasattr(v, "to") else v for k, v in default_adapter_state.items()}
    load_result = set_peft_model_state_dict(model, restore, adapter_name="default")
    logger.info("✅ LoRA reset for task adaptation (peft load_result=%s)", load_result)

    model = FastLanguageModel.for_training(model)
    model.config._attn_implementation = "eager"

    rows = build_task_training_rows(
        task_payload,
        formatter,
        n_augmentations=int(adaptation.n_training_augmentations),
        augment_seed=int(adaptation.training_augment_seed),
        max_seq_length=int(max_seq_length),
    )
    if not rows:
        model = FastLanguageModel.for_inference(model)
        model.config._attn_implementation = "eager"
        model.eval()
        logger.warning("⚠️ Task adaptation skipped: no training rows (empty train?).")
        return ({"status": "skipped", "reason": "no_training_rows", "backend": "unsloth"}, model)

    user_id, assistant_id, eos_id = _resolve_collator_token_ids(tokenizer, formatter)
    collator = QwenDataCollatorForCompletionOnlyLM(
        tokenizer=tokenizer,
        mlm=False,
        user_id=user_id,
        assistant_id=assistant_id,
        eos_id=eos_id,
    )

    output_dir = tempfile.mkdtemp(prefix="arc_unsloth_adapt_")
    train_args = dict(
        output_dir=output_dir,
        per_device_eval_batch_size=1,
        per_device_train_batch_size=max(1, int(adaptation.batch_size)),
        gradient_accumulation_steps=max(1, int(adaptation.gradient_accumulation_steps)),
        num_train_epochs=max(1, int(adaptation.num_train_epochs)),
        warmup_steps=int(adaptation.warmup_steps),
        warmup_ratio=float(adaptation.warmup_ratio),
        max_grad_norm=float(adaptation.max_grad_norm),
        learning_rate=float(adaptation.learning_rate),
        optim=str(adaptation.optim),
        weight_decay=float(adaptation.weight_decay),
        lr_scheduler_type=str(adaptation.lr_scheduler_type),
        seed=42,
        report_to="none",
        save_strategy="no",
        eval_strategy="no",
        logging_strategy="no",
        fp16=False,
        bf16=False,
        fsdp="",
        ddp_find_unused_parameters=False,
        dataloader_num_workers=0,
        gradient_checkpointing=False,
        half_precision_backend="cpu_amp",
        no_cuda=False,
    )
    filtered = dict(train_args)
    try:
        uta = UnslothTrainingArguments(**filtered)
    except TypeError:
        filtered.pop("eval_strategy", None)
        filtered["evaluation_strategy"] = "no"
        try:
            uta = UnslothTrainingArguments(**filtered)
        except TypeError:
            uta = UnslothTrainingArguments(**{k: v for k, v in filtered.items() if k != "evaluation_strategy"})

    ds = datasets.Dataset.from_list(rows)
    TrainerCls = _unsloth_fixed_trainer_class()
    trainer = TrainerCls(
        model=model,
        tokenizer=tokenizer,
        data_collator=collator,
        train_dataset=ds,
        dataset_text_field="text",
        max_seq_length=int(max_seq_length),
        args=uta,
    )

    stats: Any = None
    try:
        with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
            stats = trainer.train()
        model = trainer.accelerator.unwrap_model(trainer.model, keep_fp32_wrapper=False)
    finally:
        del trainer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    model = FastLanguageModel.for_inference(model)
    model.config._attn_implementation = "eager"
    model.eval()

    logger.info("✅ LoRA task adaptation finished (train_report=%s)", stats)
    meta = {
        "status": "ok",
        "backend": "unsloth",
        "train_report": str(stats) if stats is not None else "",
        "num_rows": len(rows),
    }
    return meta, model


def restore_peft_adapter_baseline(model: Any, default_adapter_state: dict[str, Any]) -> Any:
    """Reload PEFT ``default`` adapter from a snapshot and return an inference-ready Unsloth model.

    Does not alter base pretrained weights — only task LoRA deltas are replaced (reference reset pattern).
    """
    if not default_adapter_state:
        return model
    peft = importlib.import_module("peft")
    unsloth = importlib.import_module("unsloth")
    set_peft_model_state_dict = getattr(peft, "set_peft_model_state_dict")
    FastLanguageModel = getattr(unsloth, "FastLanguageModel")
    device = next(model.parameters()).device
    restore = {k: v.to(device) if hasattr(v, "to") else v for k, v in default_adapter_state.items()}
    set_peft_model_state_dict(model, restore, adapter_name="default")
    model = FastLanguageModel.for_inference(model)
    model.config._attn_implementation = "eager"
    model.eval()
    return model
