import pandas as pd
from sqlalchemy import create_engine, text
import os
import json
from pathlib import Path
from typing import Union, Optional, Dict


try:
    os.add_dll_directory("C:\\Program Files\\IBM\\SQLLIB\\BIN")
except AttributeError:
    # Ignore errors, such as this method not existing in older Python versions
    pass


def _open_sql_query(sql_query: Union[str, Path]) -> str:
    if isinstance(sql_query, Path) and os.path.exists(sql_query):
        with open(sql_query, 'r') as f:
            sql_query = f.read()
    if not isinstance(sql_query, str):
        raise ValueError("sql_query must be a string.")
    return sql_query


def _open_db_config(db_config: Union[Dict[str, str], Path]) -> Dict[str, str]:
    if isinstance(db_config, Path) and os.path.exists(db_config):
        with open(db_config, 'r') as f:
            db_config = json.load(f)
    if not isinstance(db_config, dict):
        raise ValueError("db_config must be a dictionary.")
    return db_config


def _run_sql_query(sql_query: str, db_config: dict) -> pd.DataFrame:
    connection_string = f"ibm_db_sa://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
    engine = create_engine(connection_string)

    with engine.connect() as connection:
        connection.execute(text(f"SET SCHEMA {db_config['schema']}"))
        df = pd.read_sql(sql_query, con=connection)
            
    return df


def run_sql_query(sql_query: Union[str, Path], db_config: Union[dict, Path], output_path: Optional[Path] = None) -> Optional[pd.DataFrame]:
    """
    Main function to execute an SQL query.

    ## Parameters:
    - sql_query: str  
        SQL query as a string or the path to a file containing the SQL query.
    - db_config: dict or path  
        Database configuration as a dictionary or the path to a JSON file containing the configuration.
    - output_path: str, optional  
        The file path where the query result will be saved in Parquet format. 
        If `None`, the function returns the resulting DataFrame.

    ## Returns:
    - pd.DataFrame
        A DataFrame containing the query results if `output_path` is not provided; otherwise nothing is returned, and the dataframe is saved to the specified path as a parquet file.
    """
    sql_query = _open_sql_query(sql_query)
    db_config = _open_db_config(db_config)
    df = _run_sql_query(sql_query, db_config)

    if output_path:
        df.to_parquet(output_path, index=False)
    else:
        return df