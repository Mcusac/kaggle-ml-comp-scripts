"""Unsloth trainer v2 fix: bypass Unsloth's Dynamo-compiled loss via vanilla CE.

Pops labels and computes a standard PyTorch ``CrossEntropyLoss``, needed when
``torch.compile`` is active and the compiled loss path misbehaves.
"""

from unsloth import UnslothTrainer

from layers.layer_0_core.level_0 import get_torch

from layers.layer_1_competition.level_0_infra.level_0 import ddp_safe_loss

torch = get_torch()


class UnslothV2FixedTrainer(UnslothTrainer):
    """
    v2 compute_loss: bypasses Unsloth's Dynamo-compiled loss entirely by
    popping labels and computing a vanilla CrossEntropyLoss.
    """

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels", None)
        outputs = model(**inputs)

        if labels is not None:
            logits = outputs.logits
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            loss_fct = torch.nn.CrossEntropyLoss()
            loss = loss_fct(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
            )
        else:
            loss = outputs["loss"] if isinstance(outputs, dict) else outputs[0]

        loss = ddp_safe_loss(loss, self.accelerator)
        return (loss, outputs) if return_outputs else loss
