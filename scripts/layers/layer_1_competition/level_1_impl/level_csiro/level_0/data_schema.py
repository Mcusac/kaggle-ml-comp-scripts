"""CSIRO biomass competition data schema."""

from typing import Dict, List

from layers.layer_1_competition.level_0_infra.level_0 import ContestDataSchema


class CSIRODataSchema(ContestDataSchema):
    """
    CSIRO biomass competition data schema.
    
    Defines CSV column names, sample ID format, and data structure for
    the CSIRO biomass prediction competition.
    """
    
    @property
    def sample_id_column(self) -> str:
        """CSIRO sample ID column name."""
        return 'sample_id'
    
    @property
    def target_columns(self) -> List[str]:
        """CSIRO target column names (in train.csv)."""
        # CSIRO uses a single 'target' column with target_name indicating which target
        return ['target']
    
    @property
    def train_csv_columns(self) -> List[str]:
        """CSIRO train.csv expected columns."""
        return [
            'sample_id',
            'image_path',
            'Sampling_Date',
            'State',
            'Species',
            'Pre_GSHH_NDVI',
            'Height_Ave_cm',
            'target_name',
            'target'
        ]
    
    @property
    def test_csv_columns(self) -> List[str]:
        """CSIRO test.csv expected columns."""
        return [
            'sample_id',
            'image_path',
            'target_name'
        ]
    
    @property
    def metadata_columns(self) -> List[str]:
        """CSIRO metadata columns (non-target columns)."""
        return [
            'image_id',
            'image_path',
            'Sampling_Date',
            'State',
            'Species',
            'Pre_GSHH_NDVI',
            'Height_Ave_cm'
        ]
    
    @property
    def image_path_column(self) -> str:
        """CSIRO image path column name."""
        return 'image_path'
    
    @property
    def target_name_column(self) -> str:
        """CSIRO target name column name."""
        return 'target_name'
    
    @property
    def target_value_column(self) -> str:
        """CSIRO target value column name."""
        return 'target'
    
    @property
    def rows_per_image_in_test(self) -> int:
        """CSIRO test.csv has 5 rows per image (one per target)."""
        return 5
    
    def validate_sample_id(self, sample_id: str) -> bool:
        """
        Validate CSIRO sample ID format: {image_id}__{target_name}
        
        Args:
            sample_id: Sample ID string (e.g., 'ID1001187975__Dry_Green_g')
            
        Returns:
            True if valid, False otherwise
        """
        parts = sample_id.split('__', 1)
        return len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 0
    
    def parse_sample_id(self, sample_id: str) -> Dict[str, str]:
        """
        Parse CSIRO sample ID format: {image_id}__{target_name}
        
        Args:
            sample_id: Sample ID string (e.g., 'ID1001187975__Dry_Green_g')
            
        Returns:
            Dictionary with 'image_id' and 'target_name' keys
        """
        parts = sample_id.split('__', 1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid CSIRO sample_id format: {sample_id}. "
                f"Expected: {{image_id}}__{{target_name}}"
            )
        return {
            'image_id': parts[0],
            'target_name': parts[1]
        }
    
    def format_sample_id(self, image_id: str, target_name: str) -> str:
        """
        Format CSIRO sample ID: {image_id}__{target_name}
        
        Args:
            image_id: Image identifier (e.g., 'ID1001187975')
            target_name: Target name (e.g., 'Dry_Green_g')
            
        Returns:
            Formatted sample ID (e.g., 'ID1001187975__Dry_Green_g')
        """
        return f"{image_id}__{target_name}"
