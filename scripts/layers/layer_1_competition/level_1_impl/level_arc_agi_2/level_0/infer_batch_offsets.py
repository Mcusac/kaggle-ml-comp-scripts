"""Batch subkeys by augmentation family using fixed index windows (reference notebook)."""

from collections import defaultdict


def infer_group_subkeys_by_test_id(sorted_subkeys: list[str]) -> dict[str, list[str]]:
    """Map ``test_id`` (part after first underscore in key before ``.``) to ordered subkeys."""
    by_test: dict[str, list[str]] = defaultdict(list)
    for sk in sorted_subkeys:
        base = sk.split(".")[0]
        parts = base.split("_")
        tid = parts[1] if len(parts) > 1 else "0"
        by_test[tid].append(sk)
    return dict(by_test)


def infer_notebook_style_decode_batches(subkeys: list[str]) -> list[list[str]]:
    """Produce batch lists matching reference offsets (0,4 / 2,6 / 8,12 / 10,14) per test group."""
    out: list[list[str]] = []
    sorted_all = sorted(subkeys)

    def _chunk(group: list[str], offsets: tuple[int, int]) -> None:
        a, b = offsets
        batch: list[str] = []
        if a + 2 <= len(group):
            batch.extend(group[a : a + 2])
        if b + 2 <= len(group):
            batch.extend(group[b : b + 2])
        if batch:
            out.append(batch)

    groups = infer_group_subkeys_by_test_id(sorted_all)
    if not groups:
        if sorted_all:
            return [sorted_all]
        return []

    for _, group in sorted(groups.items()):
        g = sorted(group)
        _chunk(g, (0, 4))
        _chunk(g, (2, 6))
        _chunk(g, (8, 12))
        _chunk(g, (10, 14))
    if not out and sorted_all:
        out.append(sorted_all)
    return out
