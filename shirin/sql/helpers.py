"""Helper functions for SQL query execution."""

import functools
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import URL, Engine

REQUIRED_CONFIG_KEYS = ('user', 'password', 'host', 'port', 'db_name', 'schema')
PARQUET_CHUNK_ROWS = 100_000


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
    """Convert pandas extension-dtype columns to plain object columns for PyArrow.

    This prevents ArrowKeyError when saving to parquet format. Returns ``df``
    unchanged (no copy) when it has no extension columns.
    """
    ext_cols = [col for col in df.columns if pd.api.types.is_extension_array_dtype(df[col].dtype)]
    if not ext_cols:
        return df
    return df.astype({col: object for col in ext_cols})


def _validate_db_config(db_config: Dict[str, Any]) -> None:
    missing_keys = [key for key in REQUIRED_CONFIG_KEYS if key not in db_config]
    if missing_keys:
        raise KeyError(f"Missing required database config keys: {missing_keys}")
    # SET SCHEMA can't take a bind parameter, so only allow plain identifiers.
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_$#@]*', str(db_config['schema'])):
        raise ValueError(f"Invalid schema name: {db_config['schema']!r}")


@functools.lru_cache(maxsize=None)
def _add_db2_dll_directory() -> None:
    """Windows needs the DB2 client DLLs on the search path; override with DB2_DLL_DIR."""
    dll_dir = os.environ.get("DB2_DLL_DIR", r"C:\Program Files\IBM\SQLLIB\BIN")
    if hasattr(os, "add_dll_directory") and os.path.isdir(dll_dir):
        os.add_dll_directory(dll_dir)


# ponytail: one pooled engine per (connection, schema) for the process lifetime; unbounded,
# fine for a handful of configs. Add eviction/dispose if configs are generated dynamically.
@functools.lru_cache(maxsize=None)
def _get_engine(url: URL, schema: str) -> Engine:
    _add_db2_dll_directory()
    engine = create_engine(url, pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def _set_schema(dbapi_connection, _connection_record) -> None:
        # Once per physical connection instead of a round trip per query.
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET SCHEMA {schema}")
        cursor.close()

    return engine


def get_engine(db_config: Dict[str, Any]) -> Engine:
    """Return the cached DB2 engine for this config (schema set on every new connection)."""
    _validate_db_config(db_config)
    url = URL.create(
        "ibm_db_sa",
        username=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=int(db_config['port']),
        database=db_config['db_name'],
    )
    return _get_engine(url, str(db_config['schema']))


def _read_sql(sql_query: str, connection: Any, params: Optional[Dict[str, Any]], **kwargs: Any) -> Any:
    # Bind parameters use SQLAlchemy's :name style; plain strings go through untouched.
    query = text(sql_query) if params else sql_query
    return pd.read_sql(query, con=connection, params=params, **kwargs)


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
        DataFrame with query results.

    Raises:
        KeyError: If required database config keys are missing.
        ValueError: If the schema name is not a plain identifier.
    """
    with get_engine(db_config).connect() as connection:
        return _read_sql(sql_query, connection, params)


def query_to_parquet(
    sql_query: str,
    db_config: Dict[str, Any],
    output_path: Path,
    params: Optional[Dict[str, Any]] = None,
    chunk_rows: int = PARQUET_CHUNK_ROWS,
) -> None:
    """Fetch in chunks and write one parquet file, without holding the whole result in pandas.

    Chunks are kept as Arrow tables (compact) and their schemas unified, so a column
    that is all-NULL or integer in an early chunk still gets its real type from later ones.
    """
    with get_engine(db_config).connect() as connection:
        chunks: Iterator[pd.DataFrame] = _read_sql(sql_query, connection, params, chunksize=chunk_rows)
        tables = [
            pa.Table.from_pandas(convert_extension_types(chunk), preserve_index=False)
            for chunk in chunks
        ]
    # ponytail: Arrow tables for the whole result stay in memory until the single write;
    # switch to a ParquetWriter with a fixed schema if results outgrow RAM.
    pq.write_table(pa.concat_tables(tables, promote_options='permissive'), output_path)
