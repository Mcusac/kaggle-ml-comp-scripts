"""Per-task Unsloth LoRA adaptation runner (NVARC reference training loop)."""

import gc
import importlib
import io
import tempfile
from contextlib import redirect_stderr, redirect_stdout

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import UnslothFixedTrainer
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
    QwenDataCollatorForCompletionOnlyLM,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    resolve_collator_token_ids,
    build_task_training_rows,
)

logger = get_logger(__name__)

Grid = list[list[int]]


def run_unsloth_task_adaptation(
    *,
    model,
    tokenizer,
    default_adapter_state,
    task_payload,
    budget_expired,
    adaptation,
    max_seq_length,
):
    if budget_expired():
        return {"status": "skipped_budget"}, model

    torch = importlib.import_module("torch")
    unsloth = importlib.import_module("unsloth")
    peft = importlib.import_module("peft")
    datasets = importlib.import_module("datasets")

    FastLanguageModel = unsloth.FastLanguageModel
    UnslothTrainingArguments = unsloth.UnslothTrainingArguments
    set_peft_model_state_dict = peft.set_peft_model_state_dict

    formatter = ArcQwenGridChatFormatter(tokenizer=tokenizer)

    restore = {
        k: v.to(model.device) if hasattr(v, "to") else v
        for k, v in default_adapter_state.items()
    }

    set_peft_model_state_dict(model, restore, adapter_name="default")

    model = FastLanguageModel.for_training(model)

    rows = build_task_training_rows(
        task_payload,
        formatter,
        n_augmentations=adaptation.n_training_augmentations,
        augment_seed=adaptation.training_augment_seed,
        max_seq_length=max_seq_length,
    )

    if not rows:
        return {"status": "skipped"}, model

    user_id, assistant_id, eos_id = resolve_collator_token_ids(
        tokenizer,
        formatter,
    )

    collator = QwenDataCollatorForCompletionOnlyLM(
            tokenizer,
            mlm=False,
            user_token_id=user_id,
            assistant_token_id=assistant_id,
            eos_token_id=eos_id,
        )

    ds = datasets.Dataset.from_list(rows)

    args = UnslothTrainingArguments(
        output_dir=tempfile.mkdtemp(),
        per_device_train_batch_size=adaptation.batch_size,
        gradient_accumulation_steps=adaptation.gradient_accumulation_steps,
        num_train_epochs=adaptation.num_train_epochs,
        learning_rate=adaptation.learning_rate,
        report_to="none",
        save_strategy="no",
        logging_strategy="no",
    )

    trainer = UnslothFixedTrainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=collator,
        train_dataset=ds,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        args=args,
    )

    with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
        trainer.train()

    model = trainer.accelerator.unwrap_model(trainer.model)

    del trainer
    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    model = FastLanguageModel.for_inference(model)
    model.eval()

    return {"status": "ok", "num_rows": len(rows)}, model
