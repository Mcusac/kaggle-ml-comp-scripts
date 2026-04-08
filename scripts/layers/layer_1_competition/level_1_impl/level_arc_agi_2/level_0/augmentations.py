"""ARC geometric/color augmentations with invertible specs."""

import random
from dataclasses import dataclass
from typing import Iterable


Grid = list[list[int]]


@dataclass(frozen=True)
class AugmentationSpec:
    """Invertible grid transform spec."""

    transpose: bool = False
    rot_k: int = 0
    color_permutation: tuple[int, ...] = tuple(range(10))

    def __post_init__(self) -> None:
        if len(self.color_permutation) != 10:
            raise ValueError("color_permutation must contain exactly 10 colors.")
        values = tuple(int(v) for v in self.color_permutation)
        if set(values) != set(range(10)):
            raise ValueError("color_permutation must be a permutation of 0..9.")
        if int(self.rot_k) not in (0, 1, 2, 3):
            raise ValueError("rot_k must be in {0,1,2,3}.")


IDENTITY_AUGMENTATION = AugmentationSpec()


def _copy_grid(grid: Grid) -> Grid:
    return [list(row) for row in grid]


def _transpose_grid(grid: Grid) -> Grid:
    if not grid:
        return []
    w = len(grid[0])
    if any(len(row) != w for row in grid):
        raise ValueError("All grid rows must have equal length.")
    return [[int(grid[r][c]) for r in range(len(grid))] for c in range(w)]


def _rotate90(grid: Grid) -> Grid:
    if not grid:
        return []
    h = len(grid)
    w = len(grid[0])
    if any(len(row) != w for row in grid):
        raise ValueError("All grid rows must have equal length.")
    return [[int(grid[h - 1 - r][c]) for r in range(h)] for c in range(w)]


def _apply_color_permutation(grid: Grid, permutation: tuple[int, ...]) -> Grid:
    return [[int(permutation[int(v) % 10]) for v in row] for row in grid]


def invert_color_permutation(permutation: tuple[int, ...]) -> tuple[int, ...]:
    inv = [0] * 10
    for idx, value in enumerate(permutation):
        inv[int(value)] = int(idx)
    return tuple(inv)


def apply_augmentation(grid: Grid, spec: AugmentationSpec) -> Grid:
    out = _copy_grid(grid)
    if spec.transpose:
        out = _transpose_grid(out)
    for _ in range(int(spec.rot_k) % 4):
        out = _rotate90(out)
    return _apply_color_permutation(out, spec.color_permutation)


def invert_augmentation(grid: Grid, spec: AugmentationSpec) -> Grid:
    out = _apply_color_permutation(grid, invert_color_permutation(spec.color_permutation))
    for _ in range((4 - (int(spec.rot_k) % 4)) % 4):
        out = _rotate90(out)
    if spec.transpose:
        out = _transpose_grid(out)
    return out


def _random_color_permutation(rng: random.Random) -> tuple[int, ...]:
    values = list(range(10))
    rng.shuffle(values)
    return tuple(values)


def _sample_transform_pairs() -> Iterable[tuple[bool, int]]:
    for transpose in (False, True):
        for rot_k in (0, 1, 2, 3):
            yield transpose, rot_k


def generate_augmentation_specs(
    n: int,
    *,
    seed: int = 0,
    include_identity: bool = True,
) -> list[AugmentationSpec]:
    """Create deterministic augmentation specs for TTA."""
    count = max(1, int(n or 1))
    rng = random.Random(int(seed))
    transforms = list(_sample_transform_pairs())
    specs: list[AugmentationSpec] = []
    if include_identity:
        specs.append(IDENTITY_AUGMENTATION)
    while len(specs) < count:
        transpose, rot_k = transforms[rng.randrange(len(transforms))]
        perm = _random_color_permutation(rng)
        spec = AugmentationSpec(transpose=transpose, rot_k=rot_k, color_permutation=perm)
        if spec in specs:
            continue
        specs.append(spec)
    return specs[:count]
