"""Configuration management for the vendor performance analysis application."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_PATH = DATA_DIR / "raw"
    PROCESSED_DATA_PATH = DATA_DIR / "processed"
    SQL_DIR = BASE_DIR / "sql"
    LOGS_DIR = BASE_DIR / "logs"
    CONFIG_FILE = BASE_DIR / "config.yaml"
    
    # Create necessary directories
    for directory in [DATA_DIR, RAW_DATA_PATH, PROCESSED_DATA_PATH, LOGS_DIR]:
        directory.mkdir(exist_ok=True, parents=True)
    
    # Database Configuration
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER = os.getenv("DB_SERVER", "localhost")
    DB_NAME = os.getenv("DB_NAME", "vendor_analytics")
    DB_USER = os.getenv("DB_USER", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "YourPassword123!")
    DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))
    
    # Application Configuration
    APP_NAME = "Vendor Performance Analysis"
    APP_VERSION = "1.0.0"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Pipeline Configuration
    BATCH_SIZE = 1000
    LOOKBACK_DAYS = 90
    INCREMENTAL_MODE = True
    VALIDATION_ENABLED = True
    ANOMALY_DETECTION = True
    
    # KPI Thresholds
    DEFECT_RATE_THRESHOLD = 5.0  # %
    LEAD_TIME_THRESHOLD = 3  # days
    COST_VARIANCE_THRESHOLD = 10.0  # %
    
    @classmethod
    def load_yaml_config(cls) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Generate SQL Server connection string."""
        return (
            f"Driver={{{cls.DB_DRIVER}}};"
            f"Server={cls.DB_SERVER};"
            f"Database={cls.DB_NAME};"
            f"UID={cls.DB_USER};"
            f"PWD={cls.DB_PASSWORD};"
            f"Timeout={cls.DB_TIMEOUT};"
        )


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    DB_NAME = "vendor_analytics_test"


# Config selector
def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("APP_ENV", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)()


"""Configuration management for the vendor performance analysis application."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_PATH = DATA_DIR / "raw"
    PROCESSED_DATA_PATH = DATA_DIR / "processed"
    SQL_DIR = BASE_DIR / "sql"
    LOGS_DIR = BASE_DIR / "logs"
    CONFIG_FILE = BASE_DIR / "config.yaml"
    
    # Create necessary directories
    for directory in [DATA_DIR, RAW_DATA_PATH, PROCESSED_DATA_PATH, LOGS_DIR]:
        directory.mkdir(exist_ok=True, parents=True)
    
    # Database Configuration
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER = os.getenv("DB_SERVER", "localhost")
    DB_NAME = os.getenv("DB_NAME", "vendor_analytics")
    DB_USER = os.getenv("DB_USER", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "YourPassword123!")
    DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))
    
    # Application Configuration
    APP_NAME = "Vendor Performance Analysis"
    APP_VERSION = "1.0.0"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Pipeline Configuration
    BATCH_SIZE = 1000
    LOOKBACK_DAYS = 90
    INCREMENTAL_MODE = True
    VALIDATION_ENABLED = True
    ANOMALY_DETECTION = True
    
    # KPI Thresholds
    DEFECT_RATE_THRESHOLD = 5.0  # %
    LEAD_TIME_THRESHOLD = 3  # days
    COST_VARIANCE_THRESHOLD = 10.0  # %
    
    @classmethod
    def load_yaml_config(cls) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Generate SQL Server connection string."""
        return (
            f"Driver={{{cls.DB_DRIVER}}};"
            f"Server={cls.DB_SERVER};"
            f"Database={cls.DB_NAME};"
            f"UID={cls.DB_USER};"
            f"PWD={cls.DB_PASSWORD};"
            f"Timeout={cls.DB_TIMEOUT};"
        )


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    DB_NAME = "vendor_analytics_test"


# Config selector
def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("APP_ENV", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)()


# Default config instance
config = get_config()

