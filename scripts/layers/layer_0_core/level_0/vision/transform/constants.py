"""Constants for vision transform operations (preprocessing, augmentation, TTA)."""

# Default preprocessing list (empty - only nonessential operations should be listed)
# Essential operations (resize, normalize) are always applied automatically
DEFAULT_PREPROCESSING_LIST = []

# Available preprocessing techniques
AVAILABLE_PREPROCESSING = {
    'resize',
    'normalize',
    'center_crop',
    'contrast_enhancement',
    'noise_reduction'
}

# Available augmentation techniques
AVAILABLE_AUGMENTATION = {
    'geometric_transformations',
    'color_jittering',
    'blurring',
    'noise_addition'
}

# Available TTA variants
AVAILABLE_TTA_VARIANTS = {
    'original',      # No geometric augmentation
    'h_flip',        # Horizontal flip
    'v_flip',        # Vertical flip
    'both_flips',    # Both horizontal and vertical flips
    'rotate_90',     # 90 degree rotation
    'rotate_270',    # 270 degree rotation
}

# Default TTA variants
DEFAULT_TTA_VARIANTS = [
    'original',
    'h_flip',
    'v_flip',
    'both_flips',
    'rotate_90',
    'rotate_270',
]
