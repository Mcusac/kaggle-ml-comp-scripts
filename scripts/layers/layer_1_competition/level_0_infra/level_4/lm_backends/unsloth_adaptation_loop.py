"""Generic Unsloth ``FastLanguageModel`` + completion-only LM micro-training."""

from __future__ import annotations

import gc
import importlib
import io
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import QwenDataCollatorForCompletionOnlyLM


def unsloth_train_completion_lm(
    *,
    model: Any,
    tokenizer: Any,
    rows: list[dict[str, Any]],
    user_token_id: int,
    assistant_token_id: int,
    eos_token_id: int,
    max_seq_length: int,
    per_device_train_batch_size: int,
    gradient_accumulation_steps: int,
    num_train_epochs: int,
    learning_rate: float,
) -> Any:
    """Run a short training loop and return ``model`` in inference mode."""
    torch = importlib.import_module("torch")
    unsloth = importlib.import_module("unsloth")
    datasets = importlib.import_module("datasets")

    from layers.layer_1_competition.level_0_infra.level_0.lm import UnslothFixedTrainer

    FastLanguageModel = unsloth.FastLanguageModel
    UnslothTrainingArguments = unsloth.UnslothTrainingArguments

    model = FastLanguageModel.for_training(model)

    collator = QwenDataCollatorForCompletionOnlyLM(
        tokenizer,
        mlm=False,
        user_token_id=user_token_id,
        assistant_token_id=assistant_token_id,
        eos_token_id=eos_token_id,
    )

    ds = datasets.Dataset.from_list(rows)

    args = UnslothTrainingArguments(
        output_dir=tempfile.mkdtemp(),
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
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
    return model