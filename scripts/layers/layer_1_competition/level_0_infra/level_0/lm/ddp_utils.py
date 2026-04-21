"""DDP-safe loss scaling for multi-process training."""


def ddp_safe_loss(loss, accelerator):
    """Clone loss tensor (view → independent) then scale for DDP."""
    if hasattr(loss, "clone"):
        loss = loss.clone()
    if accelerator.num_processes > 1:
        loss = loss * accelerator.num_processes
    return loss