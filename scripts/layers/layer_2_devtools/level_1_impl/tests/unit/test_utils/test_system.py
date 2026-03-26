"""Tests for system utilities."""

import pytest

torch = pytest.importorskip("torch", exc_type=ImportError)
import numpy as np

from utils.system import (
    set_seed,
    get_device,
    get_device_name,
    is_kaggle,
    get_environment,
    setup_environment,
    get_output_path,
    get_data_root_path,
    get_best_model_path,
    run_command,
    run_command_with_streaming,
    estimate_memory_mb,
    get_available_memory_mb,
)


def test_set_seed():
    """Test seed setting for reproducibility."""
    import random
    import numpy as np
    
    set_seed(42)
    
    # Generate some random numbers
    py_random = random.random()
    np_random = np.random.rand()
    torch_random = torch.rand(1).item()
    
    # Reset seed and verify same numbers
    set_seed(42)
    
    assert random.random() == py_random
    assert np.random.rand() == np_random
    assert torch.rand(1).item() == torch_random


def test_get_device_auto():
    """Test automatic device detection."""
    device = get_device('auto')
    
    assert isinstance(device, torch.device)
    assert device.type in ['cuda', 'cpu']


def test_get_device_explicit():
    """Test explicit device specification."""
    device = get_device('cpu')
    
    assert device.type == 'cpu'


def test_get_device_name():
    """Test device name retrieval."""
    device_name = get_device_name('cpu')
    
    assert isinstance(device_name, str)
    assert device_name == 'cpu'


def test_is_kaggle():
    """Test Kaggle environment detection."""
    # This will return False in local environment
    is_kaggle_env = is_kaggle()
    
    assert isinstance(is_kaggle_env, bool)


def test_get_environment():
    """Test environment detection."""
    env = get_environment()
    
    assert isinstance(env, str)
    assert env in ['kaggle', 'local', 'colab']


def test_setup_environment():
    """Test environment setup."""
    # Should not raise
    setup_environment()


def test_estimate_memory_mb():
    """Test memory estimation for numpy arrays."""
    # Create a test array
    arr = np.zeros((100, 100), dtype=np.float32)
    
    memory_mb = estimate_memory_mb(arr)
    
    assert isinstance(memory_mb, float)
    assert memory_mb > 0
    # float32: 100 * 100 * 4 bytes = 40,000 bytes ≈ 0.038 MB
    assert memory_mb < 1.0  # Should be small


def test_get_available_memory_mb():
    """Test available memory retrieval."""
    available_mb = get_available_memory_mb()
    
    assert isinstance(available_mb, float)
    assert available_mb > 0  # Should have some memory available


def test_get_output_path():
    """Test output path retrieval."""
    path = get_output_path('test')
    
    assert isinstance(path, (str, type(None)))


def test_get_data_root_path():
    """Test data root path retrieval."""
    path = get_data_root_path()
    
    assert isinstance(path, (str, type(None)))


def test_get_best_model_path():
    """Test best model path retrieval."""
    # This may return None if no model exists, which is fine
    path = get_best_model_path('test_model')
    
    assert isinstance(path, (str, type(None)))


def test_all_exports_importable():
    """Test that all expected exports from utils.system are importable."""
    from utils.system import __all__
    
    # Verify all exports are actually importable
    import utils.system as system_module
    
    for export_name in __all__:
        assert hasattr(system_module, export_name), f"Export '{export_name}' not found in utils.system"


def test_memory_exports_importable():
    """Test that all memory functions are importable from utils.system.memory."""
    from utils.system.memory import (
        estimate_memory_mb,
        get_available_memory_mb,
        recover_from_oom,
        is_oom_error,
        handle_oom_error_with_retry,
        cleanup_gpu_memory,
        cleanup_dataframe_and_memory,
    )
    
    # Verify functions are callable
    assert callable(estimate_memory_mb)
    assert callable(get_available_memory_mb)
    assert callable(recover_from_oom)
    assert callable(is_oom_error)
    assert callable(handle_oom_error_with_retry)
    assert callable(cleanup_gpu_memory)
    assert callable(cleanup_dataframe_and_memory)
