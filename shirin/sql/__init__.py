"""SQL query execution utilities for IBM DB2 databases."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Union
import pandas as pd
from sqlalchemy import create_engine, text


try:
    os.add_dll_directory("C:\\Program Files\\IBM\\SQLLIB\\BIN")
except AttributeError:
    # Ignore errors for older Python versions without add_dll_directory
    pass


def _load_sql_query(sql_query: Union[str, Path]) -> str:
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


def _load_db_config(
    db_config: Union[Dict[str, str], Path]
) -> Dict[str, str]:
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


def _execute_query(sql_query: str, db_config: Dict[str, str]) -> pd.DataFrame:
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


def run_sql_query(
    sql_query: Union[str, Path],
    db_config: Union[Dict[str, str], Path],
    output_path: Optional[Path] = None
) -> Optional[pd.DataFrame]:
    """Execute SQL query against IBM DB2 database.

    Args:
        sql_query: SQL query as string or Path to SQL file.
        db_config: Database configuration dict or Path to JSON config file.
                   Required keys: user, password, host, port, db_name, schema.
        output_path: Optional Path to save results as Parquet file.
                     If None, returns DataFrame.

    Returns:
        DataFrame with query results if output_path is None,
        otherwise None (results saved to file).

    Raises:
        ValueError: If sql_query or db_config format is invalid.
        KeyError: If required database config keys are missing.

    Examples:
        >>> # Execute query and get DataFrame
        >>> df = run_sql_query("SELECT * FROM table", db_config)
        >>>
        >>> # Execute query and save to file
        >>> run_sql_query(
        ...     Path("query.sql"),
        ...     Path("db_config.json"),
        ...     output_path=Path("results.parquet")
        ... )
    """
    query_string = _load_sql_query(sql_query)
    config_dict = _load_db_config(db_config)
    df = _execute_query(query_string, config_dict)

    if output_path:
        df.to_parquet(output_path, index=False)
        return None

    return df