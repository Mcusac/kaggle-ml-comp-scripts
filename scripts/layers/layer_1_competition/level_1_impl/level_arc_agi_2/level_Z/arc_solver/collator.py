"""
Data collator that masks loss on everything except assistant reply tokens.
Shared across all solver variants.
"""

import numpy as np

from typing import Any, Union
from transformers import DataCollatorForLanguageModeling

from .constants import USER_TOKEN_ID, ASSISTANT_TOKEN_ID, EOS_ID


class QwenDataCollatorForCompletionOnlyLM(DataCollatorForLanguageModeling):
    """
    Masks labels so that loss is only computed on assistant reply tokens,
    not on system/user prompt tokens.
    """

    def torch_call(self, examples: list[Union[list[int], Any, dict[str, Any]]]) -> dict[str, Any]:
        batch = super().torch_call(examples)
        for i in range(len(examples)):
            labels = batch["input_ids"][i].clone()
            user_start_idx = np.where(labels == USER_TOKEN_ID)[0].tolist()
            assistant_start_idx = np.where(labels == ASSISTANT_TOKEN_ID)[0].tolist()
            start_idx = sorted(user_start_idx + assistant_start_idx)
            end_idx = np.where(labels == EOS_ID)[0]
            batch["labels"][i, :] = -100
            for j, (start, end) in enumerate(zip(start_idx, end_idx)):
                assert start < end
                if j % 2 == 1:
                    start += 2
                    end += 1
                    batch["labels"][i, start:end] = labels[start:end]
        return batch