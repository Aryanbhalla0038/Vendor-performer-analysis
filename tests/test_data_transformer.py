"""Tests for data transformer module."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pipeline.data_transformer import DataTransformer


class TestDataTransformer:
    """Test DataTransformer class."""
    
    def test_transform_deliveries(self, test_config, sample_deliveries_df):
        """Test delivery data transformation."""
        transformer = DataTransformer(test_config)
        
        # Create test dataframe
        df = pd.DataFrame({
            'delivery_id': [1, 2],
            'po_id': [1, 2],
            'vendor_id': [1, 2],
            'scheduled_delivery_date': ['2025-12-20', '2025-12-25'],
            'actual_delivery_date': ['2025-12-20', '2025-12-26']
        })
        
        result = transformer.transform_deliveries(df)
        
        assert 'is_on_time' in result.columns
        assert 'days_late' in result.columns
        assert result['is_on_time'].iloc[0] == True
        assert result['is_on_time'].iloc[1] == False
    
    def test_quality_defect_rate_calculation(self, test_config):
        """Test quality defect rate calculation."""
        transformer = DataTransformer(test_config)
        
        df = pd.DataFrame({
            'inspection_id': [1, 2],
            'delivery_id': [1, 2],
            'vendor_id': [1, 2],
            'inspection_date': ['2025-12-21', '2025-12-27'],
            'defect_count': [5, 10],
            'total_items': [100, 100]
        })
        
        result = transformer.transform_quality_data(df)
        
        assert 'defect_rate' in result.columns
        assert result['defect_rate'].iloc[0] == 5.0
        assert result['defect_rate'].iloc[1] == 10.0
    
    def test_remove_duplicates(self, test_config):
        """Test duplicate removal."""
        transformer = DataTransformer(test_config)
        
        df = pd.DataFrame({
            'vendor_id': [1, 1, 2, 2],
            'vendor_name': ['A', 'A', 'B', 'B']
        })
        
        result = DataTransformer.remove_duplicates(df, subset=['vendor_id'])
        
        assert len(result) == 2
