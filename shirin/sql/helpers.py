"""Helper functions for SQL query execution."""

import json
from pathlib import Path
from typing import Dict, Union
import pandas as pd
from sqlalchemy import create_engine, text


def load_sql_query(sql_query: Union[str, Path]) -> str:
    """Load SQL query from string or file.
    
    Args:
        sql_query: SQL query as string or Path to SQL file.
        
    Returns:
        SQL query string.
        
    Raises:
        ValueError: If sql_query format is invalid or file not found.
    """
    if isinstance(sql_query, Path):
        if not sql_query.exists():
            raise ValueError(
                f"SQL file not found: {sql_query}"
            )
        with open(sql_query, 'r', encoding='utf-8') as f:
            return f.read()

    if isinstance(sql_query, str):
        return sql_query

    raise ValueError(
        "sql_query must be a string or Path object."
    )


def load_db_config(
    db_config: Union[Dict[str, str], Path]
) -> Dict[str, str]:
    """Load database configuration from dict or JSON file.
    
    Args:
        db_config: Database configuration dict or Path to JSON config file.
        
    Returns:
        Database configuration dictionary.
        
    Raises:
        ValueError: If db_config format is invalid or file not found.
    """
    if isinstance(db_config, Path):
        if not db_config.exists():
            raise ValueError(
                f"Database config file not found: {db_config}"
            )
        with open(db_config, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        if not isinstance(loaded_config, dict):
            raise ValueError(
                "Database config file must contain a JSON object."
            )
        return loaded_config

    if isinstance(db_config, dict):
        return db_config

    raise ValueError(
        "db_config must be a dictionary or Path object."
    )


def convert_extension_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert pandas extension types to standard types for PyArrow compatibility.
    
    This prevents ArrowKeyError when saving to parquet format.
    
    Args:
        df: DataFrame with potential extension types.
        
    Returns:
        DataFrame with standard types.
    """
    df_converted = pd.DataFrame()
    
    for col in df.columns:
        dtype = df[col].dtype
        
        if pd.api.types.is_extension_array_dtype(dtype):
            if hasattr(df[col], 'to_numpy'):
                df_converted[col] = pd.Series(df[col].to_numpy(), index=df.index)
            else:
                df_converted[col] = df[col].astype(object)
        else:
            df_converted[col] = df[col]
    
    return df_converted


def execute_query(sql_query: str, db_config: Dict[str, str]) -> pd.DataFrame:
    """Execute SQL query against IBM DB2 database.
    
    Args:
        sql_query: SQL query string.
        db_config: Database configuration dict with required keys:
                   user, password, host, port, db_name, schema.
                   
    Returns:
        DataFrame with query results.
        
    Raises:
        KeyError: If required database config keys are missing.
    """
    required_keys = ['user', 'password', 'host', 'port', 'db_name', 'schema']
    missing_keys = [key for key in required_keys if key not in db_config]
    if missing_keys:
        raise KeyError(
            f"Missing required database config keys: {missing_keys}"
        )

    connection_string = (
        f"ibm_db_sa://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
    )
    engine = create_engine(connection_string)

    with engine.connect() as connection:
        connection.execute(text(f"SET SCHEMA {db_config['schema']}"))
        df = pd.read_sql(sql_query, con=connection)

    return df
