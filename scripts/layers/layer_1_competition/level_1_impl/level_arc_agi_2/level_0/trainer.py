"""
Unsloth trainer subclasses that fix the view-tensor / Dynamo compiled loss issues.

Two variants are provided:

  UnslothFixedTrainer      — v1 strategy: routes through label_smoother with
                             Unsloth model detection.  See GitHub issue #2435.

  UnslothV2FixedTrainer    — v2 strategy: pops labels and computes a standard
                             PyTorch CrossEntropyLoss, fully bypassing Unsloth's
                             compiled loss path (needed when torch.compile is active).

Both share the same DDP loss-scaling fix (clone before in-place ops).
"""

from unsloth import UnslothTrainer

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()


def _ddp_safe_loss(loss, accelerator):
    """Clone loss tensor (view → independent) then scale for DDP."""
    if hasattr(loss, "clone"):
        loss = loss.clone()
    if accelerator.num_processes > 1:
        loss = loss * accelerator.num_processes
    return loss


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

        loss = _ddp_safe_loss(loss, self.accelerator)
        return (loss, outputs) if return_outputs else loss


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

        loss = _ddp_safe_loss(loss, self.accelerator)
        return (loss, outputs) if return_outputs else loss