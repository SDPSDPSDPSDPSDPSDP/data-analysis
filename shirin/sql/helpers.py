"""Helper functions for SQL query execution."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd
from sqlalchemy import text

from . import engine


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


def _read_sql(sql_query: str, connection: Any, params: Optional[Dict[str, Any]]) -> pd.DataFrame:
    # Bind parameters use SQLAlchemy's :name style; plain strings go through untouched.
    query = text(sql_query) if params else sql_query
    return pd.read_sql(query, con=connection, params=params)


def execute_query(
    sql_query: str,
    db_config: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Execute SQL query against IBM DB2 database.

    Args:
        sql_query: SQL query string. Use ``:name`` placeholders with ``params``.
        db_config: Database configuration dict with required keys:
                   user, password, host, port, db_name, schema.
        params: Optional bind parameters, e.g. ``{"year": 2024}``.

    Returns:
        DataFrame with query results. The whole result is loaded into memory;
        for large results use ``query_to_parquet`` (``output_path`` in ``run_sql_query``).

    Raises:
        KeyError: If required database config keys are missing.
        ValueError: If the schema name is not a plain identifier.
    """
    with engine.get_engine(db_config).connect() as connection:
        return _read_sql(sql_query, connection, params)
