"""Wall-clock helpers for bounded decode loops (reference notebook DFS time guards)."""

import time


def infer_epoch_now() -> float:
    return time.time()


def infer_should_stop_by_end_time(*, end_epoch: float | None) -> bool:
    if end_epoch is None:
        return False
    return time.time() >= float(end_epoch)


def infer_should_stop_inner_loop(
    *,
    loop_start_epoch: float,
    inner_budget_sec: float,
    end_epoch: float | None,
) -> bool:
    """Stop when global ``end_epoch`` passed or inner loop exceeded ``inner_budget_sec`` since ``loop_start_epoch``."""
    if infer_should_stop_by_end_time(end_epoch=end_epoch):
        return True
    return (time.time() - float(loop_start_epoch)) >= float(inner_budget_sec)
