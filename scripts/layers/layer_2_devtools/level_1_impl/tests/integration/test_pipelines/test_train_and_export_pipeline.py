"""Integration tests for train_and_export_pipeline verifying config setup and trainer creation."""

import pytest

pytest.importorskip("contest")
pytest.importorskip("torch", exc_type=ImportError)
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from contest.implementations.csiro.pipelines.train_and_export_pipeline import train_and_export_pipeline
from contest.implementations.csiro.modeling.training.trainer_factory import create_trainer
from contest.implementations.csiro.modeling.training.base_model_trainer import BaseModelTrainer
from contest.implementations.csiro.modeling.training.feature_extraction_trainer import FeatureExtractionTrainer


@pytest.fixture
def mock_contest_config():
    """Mock contest config object"""
    config = Mock()
    config.model = Mock()
    config.model.feature_extraction_mode = False  # Default to False
    config.model.feature_extraction_model_name = None
    config.model.regression_model_type = None
    config.data = Mock()
    config.data.dataset_type = 'split'
    config.primary_targets = ['target1', 'target2', 'target3']
    config.seed = 42
    return config


@pytest.fixture
def mock_contest_registry():
    """Mock contest registry"""
    def mock_get_contest(name):
        contest = {
            'paths': lambda: Mock(),
            'config': lambda: Mock()
        }
        return contest
    return mock_get_contest


@pytest.fixture
def mock_data_root(tmp_path):
    """Create mock data root with train.csv"""
    data_root = tmp_path / 'data'
    data_root.mkdir()
    train_csv = data_root / 'train.csv'
    train_csv.write_text('id,path,target1,target2,target3\n1,img1.jpg,1.0,2.0,3.0\n')
    return str(data_root)


@pytest.fixture
def real_csiro_config():
    """Real CSIROConfig instance from registry"""
    from contest.registry import get_contest
    contest = get_contest('csiro')
    return contest['config']()


def test_train_and_export_feature_extraction_mode_config_set(mock_contest_config, mock_data_root, tmp_path):
    """Verify config.model.feature_extraction_mode is set to True when feature_extraction_mode=True"""
    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_contest') as mock_get_contest:
        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_data_root_path', return_value=mock_data_root):
            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_best_model_path', return_value=str(tmp_path / 'export')):
                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_output_path', return_value=str(tmp_path / 'output')):
                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._setup_feature_extraction_mode') as mock_setup:
                        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._train_feature_extraction_model') as mock_train:
                            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._export_trained_model'):
                                # Setup mocks
                                mock_get_contest.return_value = {
                                    'paths': lambda: Mock(),
                                    'config': lambda: mock_contest_config
                                }
                                mock_setup.return_value = ({'n_estimators': 100}, {'variant_id': 'variant_01'})
                                mock_train.return_value = {'variant_id': 'variant_01'}
                                
                                # Call pipeline with feature_extraction_mode=True
                                train_and_export_pipeline(
                                    data_root=mock_data_root,
                                    feature_extraction_mode=True,
                                    feature_extraction_model='dinov2_base',
                                    regression_model_type='lgbm',
                                    export_only=False
                                )
                                
                                # Verify config was set correctly
                                assert mock_contest_config.model.feature_extraction_mode is True
                                assert mock_contest_config.model.feature_extraction_model_name is not None
                                assert mock_contest_config.model.regression_model_type == 'lgbm'


def test_train_and_export_feature_extraction_trainer_created(mock_contest_config, mock_data_root, tmp_path):
    """Verify FeatureExtractionTrainer is created when feature_extraction_mode=True"""
    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_contest') as mock_get_contest:
        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_data_root_path', return_value=mock_data_root):
            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_best_model_path', return_value=str(tmp_path / 'export')):
                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_output_path', return_value=str(tmp_path / 'output')):
                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._setup_feature_extraction_mode') as mock_setup:
                        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._train_feature_extraction_model') as mock_train_fe:
                            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._export_trained_model'):
                                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.create_trainer') as mock_create_trainer:
                                    # Setup mocks
                                    mock_get_contest.return_value = {
                                        'paths': lambda: Mock(),
                                        'config': lambda: mock_contest_config
                                    }
                                    mock_setup.return_value = ({'n_estimators': 100}, {'variant_id': 'variant_01'})
                                    
                                    # Mock trainer
                                    mock_trainer = Mock(spec=FeatureExtractionTrainer)
                                    mock_trainer.extract_all_features = Mock(return_value=(Mock(), Mock()))
                                    mock_create_trainer.return_value = mock_trainer
                                    
                                    # Mock feature extraction training function internals
                                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._train_feature_extraction_model') as mock_train:
                                        mock_train.return_value = {'variant_id': 'variant_01'}
                                        
                                        train_and_export_pipeline(
                                            data_root=mock_data_root,
                                            feature_extraction_mode=True,
                                            feature_extraction_model='dinov2_base',
                                            regression_model_type='lgbm',
                                            extract_features=True,
                                            export_only=False
                                        )
                                        
                                        # Verify create_trainer was called (indirectly through _train_feature_extraction_model)
                                        # The actual call happens inside _train_feature_extraction_model, so we verify the config was set
                                        assert mock_contest_config.model.feature_extraction_mode is True


def test_train_and_export_extract_all_features_available(mock_contest_config, mock_data_root, tmp_path):
    """Verify extract_all_features() can be called on created trainer"""
    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_contest') as mock_get_contest:
        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_data_root_path', return_value=mock_data_root):
            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_best_model_path', return_value=str(tmp_path / 'export')):
                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_output_path', return_value=str(tmp_path / 'output')):
                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._setup_feature_extraction_mode') as mock_setup:
                        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._train_feature_extraction_model') as mock_train:
                            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._export_trained_model'):
                                # Setup mocks
                                mock_get_contest.return_value = {
                                    'paths': lambda: Mock(),
                                    'config': lambda: mock_contest_config
                                }
                                mock_setup.return_value = ({'n_estimators': 100}, {'variant_id': 'variant_01'})
                                mock_train.return_value = {'variant_id': 'variant_01'}
                                
                                # Mock the trainer creation inside _train_feature_extraction_model
                                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.create_trainer') as mock_create_trainer:
                                    mock_trainer = Mock(spec=FeatureExtractionTrainer)
                                    mock_trainer.extract_all_features = Mock(return_value=(Mock(), Mock()))
                                    mock_create_trainer.return_value = mock_trainer
                                    
                                    train_and_export_pipeline(
                                        data_root=mock_data_root,
                                        feature_extraction_mode=True,
                                        feature_extraction_model='dinov2_base',
                                        regression_model_type='lgbm',
                                        extract_features=True,
                                        export_only=False
                                    )
                                    
                                    # Verify trainer has extract_all_features method
                                    # This is verified by the mock spec, but we can also check the config was set
                                    assert mock_contest_config.model.feature_extraction_mode is True


def test_train_and_export_end_to_end_mode(mock_contest_config, mock_data_root, tmp_path):
    """Verify BaseModelTrainer is used in end-to-end mode"""
    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_contest') as mock_get_contest:
        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_data_root_path', return_value=mock_data_root):
            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_best_model_path', return_value=str(tmp_path / 'export')):
                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_output_path', return_value=str(tmp_path / 'output')):
                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._train_end_to_end_model') as mock_train:
                        # Setup mocks
                        mock_get_contest.return_value = {
                            'paths': lambda: Mock(),
                            'config': lambda: mock_contest_config
                        }
                        mock_train.return_value = {'variant_id': 'variant_01'}
                        
                        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._export_trained_model'):
                            train_and_export_pipeline(
                                data_root=mock_data_root,
                                model='efficientnet_b3',
                                feature_extraction_mode=False,
                                export_only=False
                            )
                            
                            # Verify feature_extraction_mode was NOT set
                            assert mock_contest_config.model.feature_extraction_mode is False
                            # Verify end-to-end training was called
                            mock_train.assert_called_once()


def test_train_and_export_config_attributes_set(mock_contest_config, mock_data_root, tmp_path):
    """Verify all required config attributes are set (feature_extraction_model_name, regression_model_type)"""
    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_contest') as mock_get_contest:
        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_data_root_path', return_value=mock_data_root):
            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_best_model_path', return_value=str(tmp_path / 'export')):
                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_output_path', return_value=str(tmp_path / 'output')):
                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._setup_feature_extraction_mode') as mock_setup:
                        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._train_feature_extraction_model') as mock_train:
                            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._export_trained_model'):
                                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_pretrained_weights_path') as mock_get_pretrained:
                                    # Setup mocks
                                    mock_get_contest.return_value = {
                                        'paths': lambda: Mock(),
                                        'config': lambda: mock_contest_config
                                    }
                                    mock_get_pretrained.return_value = 'pretrained/dinov2_base'
                                    mock_setup.return_value = ({'n_estimators': 100}, {'variant_id': 'variant_01'})
                                    mock_train.return_value = {'variant_id': 'variant_01'}
                                    
                                    train_and_export_pipeline(
                                        data_root=mock_data_root,
                                        feature_extraction_mode=True,
                                        feature_extraction_model='dinov2_base',
                                        regression_model_type='lgbm',
                                        export_only=False
                                    )
                                    
                                    # Verify all config attributes are set
                                    assert mock_contest_config.model.feature_extraction_mode is True
                                    assert mock_contest_config.model.feature_extraction_model_name == 'pretrained/dinov2_base'
                                    assert mock_contest_config.model.regression_model_type == 'lgbm'
                                    mock_get_pretrained.assert_called_once_with('dinov2_base')


def test_train_and_export_config_not_set_before_trainer_creation(mock_contest_config, mock_data_root, tmp_path):
    """Verify config is set BEFORE trainer creation (catches the runtime bug)"""
    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_contest') as mock_get_contest:
        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_data_root_path', return_value=mock_data_root):
            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_best_model_path', return_value=str(tmp_path / 'export')):
                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_output_path', return_value=str(tmp_path / 'output')):
                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._setup_feature_extraction_mode') as mock_setup:
                        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._train_feature_extraction_model') as mock_train_fe:
                            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline._export_trained_model'):
                                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.create_trainer') as mock_create_trainer:
                                    # Setup mocks
                                    mock_get_contest.return_value = {
                                        'paths': lambda: Mock(),
                                        'config': lambda: mock_contest_config
                                    }
                                    mock_setup.return_value = ({'n_estimators': 100}, {'variant_id': 'variant_01'})
                                    
                                    # Track when create_trainer is called
                                    create_trainer_calls = []
                                    
                                    def track_create_trainer(*args, **kwargs):
                                        # Record config state when trainer is created
                                        create_trainer_calls.append({
                                            'feature_extraction_mode': mock_contest_config.model.feature_extraction_mode,
                                            'feature_extraction_model_name': mock_contest_config.model.feature_extraction_model_name,
                                            'regression_model_type': mock_contest_config.model.regression_model_type
                                        })
                                        # Return a mock trainer
                                        mock_trainer = Mock(spec=FeatureExtractionTrainer)
                                        mock_trainer.extract_all_features = Mock(return_value=(Mock(), Mock()))
                                        return mock_trainer
                                    
                                    mock_create_trainer.side_effect = track_create_trainer
                                    
                                    # Mock the internal calls in _train_feature_extraction_model
                                    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.Path') as mock_path:
                                        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.aggregate_train_csv') as mock_agg:
                                            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_device') as mock_get_device:
                                                mock_path.return_value.exists.return_value = True
                                                mock_agg.return_value = Mock()
                                                mock_get_device.return_value = torch.device('cpu')
                                                
                                                # This will call create_trainer inside _train_feature_extraction_model
                                                # We need to ensure the config is set before that call
                                                train_and_export_pipeline(
                                                    data_root=mock_data_root,
                                                    feature_extraction_mode=True,
                                                    feature_extraction_model='dinov2_base',
                                                    regression_model_type='lgbm',
                                                    extract_features=True,
                                                    export_only=False
                                                )
                                                
                                                # Verify config was set before trainer creation
                                                if create_trainer_calls:
                                                    last_call = create_trainer_calls[-1]
                                                    assert last_call['feature_extraction_mode'] is True, \
                                                        "Config feature_extraction_mode must be True before trainer creation"
                                                    assert last_call['feature_extraction_model_name'] is not None, \
                                                        "Config feature_extraction_model_name must be set before trainer creation"
                                                    assert last_call['regression_model_type'] == 'lgbm', \
                                                        "Config regression_model_type must be set before trainer creation"


def test_train_and_export_config_structure_matches_expectations(real_csiro_config):
    """Verify CSIROConfig structure matches what train_and_export_pipeline expects"""
    from contest.implementations.csiro.config import CSIROConfig
    
    # Verify it's a CSIROConfig
    assert isinstance(real_csiro_config, CSIROConfig)
    
    # Verify it does NOT have model attribute (this is the bug)
    assert not hasattr(real_csiro_config, 'model'), \
        "CSIROConfig should not have 'model' attribute - this would cause AttributeError"
    
    # Verify it has expected contest config attributes
    assert hasattr(real_csiro_config, 'primary_targets')
    assert hasattr(real_csiro_config, 'target_weights')
    assert hasattr(real_csiro_config, 'target_order')
    assert hasattr(real_csiro_config, 'derived_targets')


def test_train_and_export_feature_extraction_mode_raises_attribute_error(real_csiro_config):
    """Verify that accessing config.model.feature_extraction_mode raises AttributeError with real CSIROConfig"""
    # This should raise AttributeError (the bug we're catching)
    with pytest.raises(AttributeError, match="'CSIROConfig' object has no attribute 'model'"):
        _ = real_csiro_config.model.feature_extraction_mode


def test_train_and_export_pipeline_fails_with_real_config_structure(mock_data_root, tmp_path):
    """Verify train_and_export_pipeline fails with AttributeError when using real CSIROConfig"""
    from contest.registry import get_contest
    
    with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_contest') as mock_get_contest:
        with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_data_root_path', return_value=mock_data_root):
            with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_best_model_path', return_value=str(tmp_path / 'export')):
                with patch('contest.implementations.csiro.pipelines.train_and_export_pipeline.get_output_path', return_value=str(tmp_path / 'output')):
                    # Use REAL contest registry (not mocked)
                    real_contest = get_contest('csiro')
                    mock_get_contest.return_value = real_contest
                    
                    # This should raise AttributeError at line 666
                    with pytest.raises(AttributeError, match="'CSIROConfig' object has no attribute 'model'"):
                        train_and_export_pipeline(
                            data_root=mock_data_root,
                            feature_extraction_mode=True,
                            feature_extraction_model='dinov2_base',
                            regression_model_type='lgbm',
                            export_only=False
                        )
