"""Unsloth trainer v1 fix: routes through ``label_smoother`` with Unsloth detection.

Fixes the view-tensor / Dynamo compiled loss issues. See:
https://github.com/unslothai/unsloth/issues/2435
"""

from unsloth import UnslothTrainer

from layers.layer_1_competition.level_0_infra.level_0 import ddp_safe_loss


class UnslothFixedTrainer(UnslothTrainer):
    """
    v1 compute_loss: delegates to label_smoother when present,
    detects Unsloth models to pass ``shift_labels=True``.

    Ref: https://github.com/unslothai/unsloth/issues/2435
    """

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        if self.label_smoother is not None and "labels" in inputs:
            labels = inputs.pop("labels")
        else:
            labels = None

        outputs = model(**inputs)

        if labels is not None:
            unwrapped = self.accelerator.unwrap_model(model)
            is_unsloth = (
                hasattr(unwrapped, "_get_name")
                and "unsloth" in unwrapped._get_name().lower()
            )
            if is_unsloth:
                loss = self.label_smoother(outputs, labels, shift_labels=True)
            else:
                loss = self.label_smoother(outputs, labels)
        else:
            loss = outputs["loss"] if isinstance(outputs, dict) else outputs[0]

        loss = ddp_safe_loss(loss, self.accelerator)
        return (loss, outputs) if return_outputs else loss
