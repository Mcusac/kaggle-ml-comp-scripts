import numpy as np

def convert_grid_to_string(grid) -> str:
    """Convert 2D numpy array to string representation."""
    return "\n".join("".join(str(int(cell)) for cell in row) for row in grid)

def is_valid_solution(array) -> bool:
    """Check if array is a valid 2D solution."""
    return isinstance(array, np.ndarray) and array.ndim == 2 and all(0 < x <= 30 for x in array.shape)