"""Tests for data loader module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pipeline.data_loader import DataLoader


class TestDataLoader:
    """Test DataLoader class."""
    
    def test_load_csv_success(self, test_config):
        """Test successful CSV loading."""
        loader = DataLoader(test_config)
        
        # This will test with actual CSV files if they exist
        try:
            df = loader.load_vendors()
            assert df is not None
            assert len(df) > 0
            assert 'vendor_id' in df.columns
        except FileNotFoundError:
            pytest.skip("Sample data files not found")
    
    def test_load_csv_file_not_found(self, test_config):
        """Test error handling for missing file."""
        loader = DataLoader(test_config)
        
        with pytest.raises(FileNotFoundError):
            loader.load_csv("nonexistent_file.csv")
    
    def test_save_processed_data(self, test_config, sample_vendors_df):
        """Test saving processed data."""
        loader = DataLoader(test_config)
        output_path = loader.save_processed_data(sample_vendors_df, "test_output.csv")
        
        assert output_path.exists()
        
        # Cleanup
        output_path.unlink()
