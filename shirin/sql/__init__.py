"""SQL query execution utilities for IBM DB2 databases."""

import os
from pathlib import Path
from typing import Dict, Optional, Union
import pandas as pd

from .helpers import (
    load_sql_query,
    load_db_config,
    convert_extension_types,
    execute_query
)


try:
    os.add_dll_directory("C:\\Program Files\\IBM\\SQLLIB\\BIN")
except AttributeError:
    # Ignore errors for older Python versions without add_dll_directory
    pass


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
    query_string = load_sql_query(sql_query)
    config_dict = load_db_config(db_config)
    df = execute_query(query_string, config_dict)

    if output_path:
        # Convert extension types to avoid PyArrow compatibility issues
        df_to_save = convert_extension_types(df)
        df_to_save.to_parquet(output_path, index=False)
        return None

    return df