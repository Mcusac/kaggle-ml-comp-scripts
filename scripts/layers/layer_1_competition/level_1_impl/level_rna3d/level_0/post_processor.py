"""Stanford RNA 3D Folding Part 2 post-processing.

Primary requirement from the dataset description: x/y/z coordinates are clipped to
[-999.999, 9999.999] before scoring (competition PDB-style coordinate range).
"""

from layers.layer_1_competition.level_0_infra.level_0 import ClipRangePostProcessor


class RNA3DPostProcessor(ClipRangePostProcessor):
    """Clips coordinate predictions to the required valid range."""

    def __init__(self, clip_min: float = -999.999, clip_max: float = 9999.999):
        super().__init__(clip_min=clip_min, clip_max=clip_max)
