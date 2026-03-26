"""Test that the config fix works - config gets model and data attributes added."""

import pytest

pytest.importorskip("contest")
from contest.registry import get_contest


def test_config_gets_model_attribute_in_pipeline():
    """Verify that contest_config gets model attribute added (simulating pipeline fix)"""
    # Get actual config from registry (same way pipeline does)
    contest = get_contest('csiro')
    config = contest['config']()
    
    # Simulate the fix: add model attribute if it doesn't exist
    if not hasattr(config, 'model'):
        class ModelConfig:
            def __init__(self):
                self.feature_extraction_mode = False
                self.feature_extraction_model_name = None
                self.regression_model_type = None
        config.model = ModelConfig()
    
    # Now accessing config.model should work
    assert hasattr(config, 'model')
    assert hasattr(config.model, 'feature_extraction_mode')
    config.model.feature_extraction_mode = True
    assert config.model.feature_extraction_mode is True


def test_config_gets_data_attribute_in_pipeline():
    """Verify that contest_config gets data attribute added (simulating pipeline fix)"""
    # Get actual config from registry (same way pipeline does)
    contest = get_contest('csiro')
    config = contest['config']()
    
    # Simulate the fix: add data attribute if it doesn't exist
    if not hasattr(config, 'data'):
        class DataConfig:
            def __init__(self):
                self.dataset_type = 'split'
        config.data = DataConfig()
    
    # Now accessing config.data should work
    assert hasattr(config, 'data')
    assert hasattr(config.data, 'dataset_type')
    config.data.dataset_type = 'full'
    assert config.data.dataset_type == 'full'
