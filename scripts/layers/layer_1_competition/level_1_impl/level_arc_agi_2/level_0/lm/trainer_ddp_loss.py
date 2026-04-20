"""Shared DDP-safe loss helper for the Unsloth trainer fixes."""


def ddp_safe_loss(loss, accelerator):
    """Clone loss tensor (view → independent) then scale for DDP."""
    if hasattr(loss, "clone"):
        loss = loss.clone()
    if accelerator.num_processes > 1:
        loss = loss * accelerator.num_processes
    return loss
