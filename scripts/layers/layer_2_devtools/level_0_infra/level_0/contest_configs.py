"""Pytest fixtures for contest configuration objects."""

import pytest
import torch

from unittest.mock import Mock


@pytest.fixture
def mock_contest_config_feature_extraction():
    """
    Mock contest config with feature_extraction_mode=True.
    
    Returns:
        Mock config object with feature extraction settings configured.
    """
    config = Mock()
    config.model = Mock()
    config.model.feature_extraction_mode = True
    config.model.feature_extraction_model_name = 'dinov2_base'
    config.model.regression_model_type = 'lgbm'
    config.data = Mock()
    config.data.dataset_type = 'split'
    config.primary_targets = ['target1', 'target2', 'target3']
    config.seed = 42
    return config


@pytest.fixture
def mock_contest_config_end_to_end():
    """
    Mock contest config with feature_extraction_mode=False (end-to-end mode).
    
    Returns:
        Mock config object for end-to-end training.
    """
    config = Mock()
    config.model = Mock()
    config.model.feature_extraction_mode = False
    config.model.model_name = 'efficientnet_b3'
    config.data = Mock()
    config.data.dataset_type = 'split'
    config.primary_targets = ['target1', 'target2', 'target3']
    config.seed = 42
    return config


@pytest.fixture
def mock_contest_config_dict_feature_extraction():
    """
    Mock contest config as dict with feature_extraction_mode=True.
    
    Returns:
        Dict config for feature extraction mode.
    """
    return {
        'feature_extraction_mode': True,
        'regression_model_type': 'lgbm',
        'dataset_type': 'split',
        'seed': 42
    }


@pytest.fixture
def mock_contest_config_dict_end_to_end():
    """
    Mock contest config as dict with feature_extraction_mode=False.
    
    Returns:
        Dict config for end-to-end training.
    """
    return {
        'feature_extraction_mode': False,
        'model_name': 'efficientnet_b3',
        'dataset_type': 'split',
        'seed': 42
    }


@pytest.fixture
def mock_device():
    """
    Mock torch device (CPU).
    
    Returns:
        torch.device('cpu')
    """
    return torch.device('cpu')


@pytest.fixture
def mock_device_cuda():
    """
    Mock torch device (CUDA).
    
    Returns:
        torch.device('cuda:0')
    """
    return torch.device('cuda:0')
