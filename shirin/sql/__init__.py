"""SQL query execution utilities for IBM DB2 databases."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd

from .helpers import (
    load_sql_query,
    load_db_config,
    execute_query,
    query_to_parquet,
)


def run_sql_query(
    sql_query: Union[str, Path],
    db_config: Union[Dict[str, Any], Path],
    output_path: Optional[Path] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Optional[pd.DataFrame]:
    """Execute SQL query against IBM DB2 database.

    Args:
        sql_query: SQL query as string or Path to SQL file.
        db_config: Database configuration dict or Path to JSON config file.
                   Required keys: user, password, host, port, db_name, schema.
        output_path: Optional Path to save results as Parquet file (fetched in chunks).
                     If None, returns DataFrame.
        params: Optional bind parameters for ``:name`` placeholders in the query,
                e.g. ``{"year": 2024}``. Prefer this over formatting values into SQL:
                DB2 reuses one cached plan instead of compiling every literal value.
                With params the query is parsed by SQLAlchemy, so a literal colon
                followed by a word (e.g. ``'12:00'``) must be escaped as ``'12\\:00'``.

    Returns:
        DataFrame with query results if output_path is None,
        otherwise None (results saved to file).

    Raises:
        ValueError: If sql_query or db_config format is invalid, or the schema
                    name is not a plain identifier.
        KeyError: If required database config keys are missing.

    Examples:
        >>> # Execute query and get DataFrame
        >>> df = run_sql_query("SELECT * FROM table", db_config)
        >>>
        >>> # With bind parameters
        >>> df = run_sql_query("SELECT * FROM t WHERE year = :year", db_config, params={"year": 2024})
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

    if output_path:
        query_to_parquet(query_string, config_dict, output_path, params=params)
        return None

    return execute_query(query_string, config_dict, params=params)
