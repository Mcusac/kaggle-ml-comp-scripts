"""Completion-only LM collator (assistant span loss); Qwen reference token IDs as defaults."""

import numpy as np

from typing import Any, Union
from transformers import DataCollatorForLanguageModeling

# Match reference NVARC / ``llm_decoding`` Qwen chat template defaults.
REFERENCE_USER_TOKEN_ID: int = 11
REFERENCE_ASSISTANT_TOKEN_ID: int = 12
REFERENCE_EOS_ID: int = 15


class QwenDataCollatorForCompletionOnlyLM(DataCollatorForLanguageModeling):
    """Masks labels so loss is only computed on assistant reply tokens.

    Token IDs default to the reference Qwen constants but can be overridden
    via constructor args when using a tokenizer with different token mappings.
    """

    def __init__(
        self,
        tokenizer: Any,
        mlm: bool = False,
        *,
        user_token_id: int = REFERENCE_USER_TOKEN_ID,
        assistant_token_id: int = REFERENCE_ASSISTANT_TOKEN_ID,
        eos_token_id: int = REFERENCE_EOS_ID,
        **kwargs: Any,
    ) -> None:
        super().__init__(tokenizer=tokenizer, mlm=mlm, **kwargs)
        self.user_token_id = int(user_token_id)
        self.assistant_token_id = int(assistant_token_id)
        self.eos_token_id = int(eos_token_id)

    def torch_call(self, examples: list[Union[list[int], Any, dict[str, Any]]]) -> dict[str, Any]:
        batch = super().torch_call(examples)
        for i in range(len(examples)):
            labels = batch["input_ids"][i].clone()
            arr = labels.cpu().numpy()
            user_start_idx = np.where(arr == self.user_token_id)[0].tolist()
            assistant_start_idx = np.where(arr == self.assistant_token_id)[0].tolist()
            start_idx = sorted(user_start_idx + assistant_start_idx)
            end_idx = np.where(arr == self.eos_token_id)[0]
            batch["labels"][i, :] = -100
            for j, (start, end) in enumerate(zip(start_idx, end_idx)):
                if j % 2 == 1:
                    batch["labels"][i, start + 2 : end + 1] = labels[start + 2 : end + 1]
        return batch