"""Tests for data validator module."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pipeline.data_validator import DataValidator


class TestDataValidator:
    """Test DataValidator class."""
    
    def test_validate_vendors_success(self, test_config, sample_vendors_df):
        """Test successful vendor validation."""
        validator = DataValidator(test_config)
        
        is_valid, errors = validator.validate_vendors(sample_vendors_df)
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_vendors_missing_columns(self, test_config):
        """Test vendor validation with missing columns."""
        validator = DataValidator(test_config)
        
        df = pd.DataFrame({
            'vendor_id': [1, 2],
            'vendor_name': ['A', 'B']
        })
        
        is_valid, errors = validator.validate_vendors(df)
        
        assert is_valid == False
        assert len(errors) > 0
    
    def test_validate_deliveries(self, test_config, sample_deliveries_df):
        """Test delivery validation."""
        validator = DataValidator(test_config)
        
        is_valid, errors = validator.validate_deliveries(sample_deliveries_df)
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_detect_anomalies(self, test_config):
        """Test anomaly detection."""
        validator = DataValidator(test_config)
        
        df = pd.DataFrame({
            'value': [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
        })
        
        result = validator.detect_anomalies(df, 'value', method='iqr')
        
        assert 'is_anomaly' in result.columns
        assert result['is_anomaly'].sum() > 0
