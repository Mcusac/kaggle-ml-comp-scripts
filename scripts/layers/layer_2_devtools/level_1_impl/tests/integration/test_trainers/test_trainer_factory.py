"""Unit tests for trainer factory verifying correct trainer selection."""

import pytest

pytest.importorskip("contest")
pytest.importorskip("torch", exc_type=ImportError)
from unittest.mock import Mock, patch, MagicMock

from contest.implementations.csiro.modeling.training.trainer_factory import create_trainer
from contest.implementations.csiro.modeling.training.base_model_trainer import BaseModelTrainer
from contest.implementations.csiro.modeling.training.feature_extraction_trainer import FeatureExtractionTrainer


@pytest.fixture
def mock_config_feature_extraction():
    """Mock config with feature_extraction_mode=True"""
    config = Mock()
    config.model = Mock()
    config.model.feature_extraction_mode = True
    config.model.feature_extraction_model_name = 'dinov2_base'
    config.model.regression_model_type = 'lgbm'
    config.data = Mock()
    config.data.dataset_type = 'split'
    config.seed = 42
    return config


@pytest.fixture
def mock_config_end_to_end():
    """Mock config with feature_extraction_mode=False"""
    config = Mock()
    config.model = Mock()
    config.model.feature_extraction_mode = False
    config.model.model_name = 'efficientnet_b3'
    config.data = Mock()
    config.data.dataset_type = 'split'
    return config


@pytest.fixture
def mock_config_dict_feature_extraction():
    """Mock config as dict with feature_extraction_mode=True"""
    return {
        'feature_extraction_mode': True,
        'regression_model_type': 'lgbm',
        'dataset_type': 'split'
    }


@pytest.fixture
def mock_device():
    """Mock torch device"""
    return torch.device('cpu')


def test_create_trainer_feature_extraction_mode_true(mock_config_feature_extraction, mock_device):
    """Verify FeatureExtractionTrainer is created when config.model.feature_extraction_mode=True"""
    with patch('contest.implementations.csiro.modeling.training.feature_extraction_trainer.FeatureExtractor') as mock_fe:
        with patch('contest.implementations.csiro.modeling.training.feature_extraction_trainer.create_regression_model') as mock_rm:
            # Mock FeatureExtractor and regression model
            mock_fe_instance = Mock()
            mock_fe.return_value = mock_fe_instance
            mock_rm.return_value = Mock()
            
            trainer = create_trainer(
                config=mock_config_feature_extraction,
                device=mock_device
            )
            
            assert isinstance(trainer, FeatureExtractionTrainer)
            assert hasattr(trainer, 'extract_all_features')
            assert trainer.config == mock_config_feature_extraction
            assert trainer.device == mock_device


def test_create_trainer_feature_extraction_mode_false(mock_config_end_to_end, mock_device):
    """Verify BaseModelTrainer is created when feature_extraction_mode=False"""
    with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_model') as mock_model:
        with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_loss_function'):
            with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_optimizer'):
                with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_scheduler'):
                    # Mock model creation
                    mock_model_instance = Mock()
                    mock_model.return_value = mock_model_instance
                    
                    trainer = create_trainer(
                        config=mock_config_end_to_end,
                        device=mock_device
                    )
                    
                    assert isinstance(trainer, BaseModelTrainer)
                    assert not hasattr(trainer, 'extract_all_features')
                    assert trainer.config == mock_config_end_to_end
                    assert trainer.device == mock_device


def test_create_trainer_config_dict(mock_config_dict_feature_extraction, mock_device):
    """Verify trainer creation works with dict config"""
    with patch('contest.implementations.csiro.modeling.training.feature_extraction_trainer.FeatureExtractor') as mock_fe:
        with patch('contest.implementations.csiro.modeling.training.feature_extraction_trainer.create_regression_model') as mock_rm:
            # Mock FeatureExtractor and regression model
            mock_fe_instance = Mock()
            mock_fe.return_value = mock_fe_instance
            mock_rm.return_value = Mock()
            
            trainer = create_trainer(
                config=mock_config_dict_feature_extraction,
                device=mock_device
            )
            
            assert isinstance(trainer, FeatureExtractionTrainer)
            assert hasattr(trainer, 'extract_all_features')


def test_create_trainer_regression_only(mock_config_feature_extraction, mock_device):
    """Verify regression_only mode creates FeatureExtractionTrainer"""
    with patch('contest.implementations.csiro.modeling.training.feature_extraction_trainer.create_regression_model') as mock_rm:
        mock_rm.return_value = Mock()
        
        trainer = create_trainer(
            config=mock_config_feature_extraction,
            device=mock_device,
            regression_only=True
        )
        
        assert isinstance(trainer, FeatureExtractionTrainer)
        assert trainer.regression_only is True
        assert trainer.feature_extractor is None


def test_create_trainer_missing_feature_extraction_mode(mock_device):
    """Verify default behavior when feature_extraction_mode attribute is missing"""
    config = Mock()
    config.model = Mock()
    # Don't set feature_extraction_mode - should default to False
    config.model.model_name = 'efficientnet_b3'
    config.data = Mock()
    config.data.dataset_type = 'split'
    
    with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_model') as mock_model:
        with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_loss_function'):
            with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_optimizer'):
                with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_scheduler'):
                    mock_model_instance = Mock()
                    mock_model.return_value = mock_model_instance
                    
                    trainer = create_trainer(
                        config=config,
                        device=mock_device
                    )
                    
                    assert isinstance(trainer, BaseModelTrainer)


def test_create_trainer_feature_extraction_has_extract_all_features(mock_config_feature_extraction, mock_device):
    """Verify FeatureExtractionTrainer has extract_all_features method"""
    with patch('contest.implementations.csiro.modeling.training.feature_extraction_trainer.FeatureExtractor') as mock_fe:
        with patch('contest.implementations.csiro.modeling.training.feature_extraction_trainer.create_regression_model') as mock_rm:
            mock_fe_instance = Mock()
            mock_fe.return_value = mock_fe_instance
            mock_rm.return_value = Mock()
            
            trainer = create_trainer(
                config=mock_config_feature_extraction,
                device=mock_device
            )
            
            assert hasattr(trainer, 'extract_all_features')
            assert callable(getattr(trainer, 'extract_all_features'))


def test_create_trainer_base_model_trainer_no_extract_all_features(mock_config_end_to_end, mock_device):
    """Verify BaseModelTrainer does NOT have extract_all_features method"""
    with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_model') as mock_model:
        with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_loss_function'):
            with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_optimizer'):
                with patch('contest.implementations.csiro.modeling.training.base_model_trainer.create_scheduler'):
                    mock_model_instance = Mock()
                    mock_model.return_value = mock_model_instance
                    
                    trainer = create_trainer(
                        config=mock_config_end_to_end,
                        device=mock_device
                    )
                    
                    assert not hasattr(trainer, 'extract_all_features')
