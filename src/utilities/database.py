"""Database management utility for SQL Server operations."""

import pandas as pd
import logging
from typing import Optional, List

# Optional SQL import
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database connections and operations."""
    
    def __init__(self, connection_string: str):
        """Initialize database manager."""
        self.connection_string = connection_string
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            logger.info("Connected to SQL Server database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from database")
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute SELECT query and return results."""
        if not self.connection:
            logger.error("No database connection")
            return None
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return None
    
    def execute_update(self, query: str) -> bool:
        """Execute INSERT/UPDATE/DELETE query."""
        if not self.connection:
            logger.error("No database connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            logger.info(f"Update query executed successfully")
            return True
        except Exception as e:
            logger.error(f"Update failed: {str(e)}")
            self.connection.rollback()
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        query = f"""
        SELECT 1 FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = '{table_name}'
        """
        result = self.execute_query(query)
        return result is not None and len(result) > 0
    
    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str) -> bool:
        """Create table from pandas DataFrame."""
        try:
            # Map pandas dtypes to SQL Server types
            type_mapping = {
                'int64': 'INT',
                'float64': 'FLOAT',
                'object': 'NVARCHAR(MAX)',
                'datetime64': 'DATETIME'
            }
            
            columns = []
            for col, dtype in zip(df.columns, df.dtypes):
                sql_type = type_mapping.get(str(dtype), 'NVARCHAR(MAX)')
                columns.append(f"[{col}] {sql_type}")
            
            create_query = f"CREATE TABLE [{table_name}] ({', '.join(columns)})"
            
            return self.execute_update(create_query)
        except Exception as e:
            logger.error(f"Failed to create table: {str(e)}")
            return False
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str) -> bool:
        """Insert DataFrame data into table."""
        try:
            cursor = self.connection.cursor()
            
            for idx, row in df.iterrows():
                columns = list(df.columns)
                values = []
                for val in row:
                    if isinstance(val, str):
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    else:
                        values.append(str(val))
                
                insert_query = (
                    f"INSERT INTO [{table_name}] ({', '.join([f'[{col}]' for col in columns])}) "
                    f"VALUES ({', '.join(values)})"
                )
                cursor.execute(insert_query)
            
            self.connection.commit()
            logger.info(f"Inserted {len(df)} rows into {table_name}")
            return True
        except Exception as e:
            logger.error(f"Insert failed: {str(e)}")
            self.connection.rollback()
            return False
