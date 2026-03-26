"""Tests for runtime configuration."""

import sys
from pathlib import Path

import pytest

# ``config`` package lives under layer_0_core/level_0 (see runtime_config.py).
_SCRIPTS_ROOT = Path(__file__).resolve().parents[6]
_LEVEL_0_DIR = _SCRIPTS_ROOT / "layers" / "layer_0_core" / "level_0"
if _LEVEL_0_DIR.is_dir() and str(_LEVEL_0_DIR) not in sys.path:
    sys.path.insert(0, str(_LEVEL_0_DIR))

from config.runtime_config import RuntimeConfig


def test_runtime_config_defaults():
    """Test RuntimeConfig default values."""
    config = RuntimeConfig()
    
    assert config.seed == 42
    assert config.device == 'auto'
    assert config.num_workers == 4
    assert config.output_dir == 'output'
    assert config.verbose is True
    assert config.debug is False


def test_runtime_config_custom_values():
    """Test RuntimeConfig with custom values."""
    config = RuntimeConfig(
        seed=123,
        device='cuda:0',
        num_workers=8,
        output_dir='custom_output'
    )
    
    assert config.seed == 123
    assert config.device == 'cuda:0'
    assert config.num_workers == 8
    assert config.output_dir == 'custom_output'


def test_runtime_config_log_dir():
    """Test automatic log_dir creation."""
    config = RuntimeConfig(output_dir='my_output')
    
    # Use Path for cross-platform path comparison
    expected_log_dir = str(Path('my_output') / 'logs')
    assert config.log_dir == expected_log_dir
    
    # Test with explicit log_dir
    config2 = RuntimeConfig(log_dir='custom_logs')
    assert config2.log_dir == 'custom_logs'
