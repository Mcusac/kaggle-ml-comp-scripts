"""Test config structure to catch AttributeError before pipeline execution."""

import pytest

pytest.importorskip("contest")
from contest.registry import get_contest
from contest.implementations.csiro.config import CSIROConfig


def test_csiro_config_structure_matches_expectations():
    """Verify CSIROConfig structure matches what train_and_export_pipeline expects"""
    # Get actual config from registry (same way pipeline does)
    contest = get_contest('csiro')
    config = contest['config']()
    
    # Verify it's a CSIROConfig
    assert isinstance(config, CSIROConfig)
    
    # Verify it does NOT have model attribute (this is the bug)
    assert not hasattr(config, 'model'), \
        "CSIROConfig should not have 'model' attribute - this would cause AttributeError"
    
    # Verify it has expected contest config attributes
    assert hasattr(config, 'primary_targets')
    assert hasattr(config, 'target_weights')
    assert hasattr(config, 'target_order')
    assert hasattr(config, 'derived_targets')


def test_csiro_config_feature_extraction_mode_raises_attribute_error():
    """Verify that accessing config.model.feature_extraction_mode raises AttributeError with real CSIROConfig"""
    # Get actual config (same as pipeline)
    contest = get_contest('csiro')
    config = contest['config']()
    
    # This should raise AttributeError (the bug we're catching)
    with pytest.raises(AttributeError, match="'CSIROConfig' object has no attribute 'model'"):
        _ = config.model.feature_extraction_mode
