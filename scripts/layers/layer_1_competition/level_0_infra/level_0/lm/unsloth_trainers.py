"""Unsloth trainer fixes for stable loss computation under compile / label smoothing."""

from unsloth import UnslothTrainer

from layers.layer_0_core.level_0 import get_torch

from .ddp_utils import ddp_safe_loss

torch = get_torch()


class UnslothFixedTrainer(UnslothTrainer):
    """v1: ``label_smoother`` path with Unsloth ``shift_labels`` detection."""

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


class UnslothV2FixedTrainer(UnslothTrainer):
    """v2: vanilla CE loss, bypassing Dynamo-compiled loss when needed."""

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


__all__ = [
    "UnslothFixedTrainer",
    "UnslothV2FixedTrainer",
]
