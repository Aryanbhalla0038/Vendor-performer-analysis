"""Data loader module for ingesting vendor data from various sources."""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Optional SQL import
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

logger = logging.getLogger(__name__)


class DataLoader:
    """Load data from CSV files and SQL Server database."""
    
    def __init__(self, config):
        """Initialize data loader with configuration."""
        self.config = config
        self.raw_data_path = config.RAW_DATA_PATH
    
    def load_csv(self, file_name: str) -> pd.DataFrame:
        """Load data from CSV file."""
        file_path = self.raw_data_path / file_name
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} rows from {file_name}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV {file_name}: {str(e)}")
            raise
    
    def load_from_sql(self, query: str) -> pd.DataFrame:
        """Load data from SQL Server database."""
        try:
            connection_string = self.config.get_connection_string()
            conn = pyodbc.connect(connection_string)
            df = pd.read_sql(query, conn)
            conn.close()
            logger.info(f"Loaded {len(df)} rows from SQL Server")
            return df
        except Exception as e:
            logger.error(f"Error loading from SQL: {str(e)}")
            raise
    
    def load_vendors(self) -> pd.DataFrame:
        """Load vendor master data."""
        return self.load_csv("vendors.csv")
    
    def load_purchase_orders(self) -> pd.DataFrame:
        """Load purchase order data."""
        return self.load_csv("purchase_orders.csv")
    
    def load_deliveries(self) -> pd.DataFrame:
        """Load delivery data."""
        return self.load_csv("deliveries.csv")
    
    def load_quality_data(self) -> pd.DataFrame:
        """Load quality inspection data."""
        return self.load_csv("quality_inspections.csv")
    
    def save_processed_data(self, df: pd.DataFrame, file_name: str) -> Path:
        """Save processed data to CSV."""
        output_path = self.config.PROCESSED_DATA_PATH / file_name
        df.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {file_name}")
        return output_path
