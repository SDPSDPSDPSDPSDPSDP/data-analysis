"""Helper functions for SQL query execution."""

import functools
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import URL, Connection, CursorResult, Engine

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
    # pool_recycle replaces a pre-ping round trip per query: connections older than 15 min
    # are reopened, which stays under typical DB2/firewall idle timeouts. One connection is
    # kept idle; up to 4 extra for concurrent callers are closed when returned.
    engine = create_engine(url, pool_recycle=900, pool_size=1, max_overflow=4)

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


def _read_sql(sql_query: str, connection: Any, params: Optional[Dict[str, Any]]) -> pd.DataFrame:
    # Bind parameters use SQLAlchemy's :name style; plain strings go through untouched.
    query = text(sql_query) if params else sql_query
    return pd.read_sql(query, con=connection, params=params)


def _execute_streaming(
    connection: Connection, sql_query: str, params: Optional[Dict[str, Any]], chunk_rows: int
) -> CursorResult:
    """Same parsing rules as _read_sql, but rows are fetched chunk_rows at a time."""
    streaming = connection.execution_options(yield_per=chunk_rows)
    if params:
        return streaming.execute(text(sql_query), params)
    return streaming.exec_driver_sql(sql_query)


def _rows_to_table(columns: List[str], rows: List[Any]) -> pa.Table:
    return pa.Table.from_arrays([pa.array(list(values)) for values in zip(*rows)], names=columns)


def _unify(tables: List[pa.Table]) -> pa.Schema:
    return pa.unify_schemas([table.schema for table in tables], promote_options='permissive')


def _widen(schema: pa.Schema) -> pa.Schema:
    """Arrow infers decimal precision per chunk; widen to the max so later chunks still fit."""
    return pa.schema([
        field.with_type(pa.decimal128(38, field.type.scale)) if pa.types.is_decimal(field.type) else field
        for field in schema
    ])


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
    with get_engine(db_config).connect() as connection:
        return _read_sql(sql_query, connection, params)


def query_to_parquet(
    sql_query: str,
    db_config: Dict[str, Any],
    output_path: Path,
    params: Optional[Dict[str, Any]] = None,
    chunk_rows: int = PARQUET_CHUNK_ROWS,
) -> None:
    """Stream the result into one parquet file, chunk_rows rows at a time, without pandas.

    The parquet schema is fixed once every column has a real type: chunks are buffered
    while a column is still all-NULL, then written, and every later chunk is cast to it.
    """
    with get_engine(db_config).connect() as connection:
        result = _execute_streaming(connection, sql_query, params, chunk_rows)
        columns = list(result.keys())
        # ponytail: a column that stays NULL for many rows keeps them all buffered in memory;
        # read types from cursor.description if that ever matters.
        pending: List[pa.Table] = []
        writer: Optional[pq.ParquetWriter] = None
        try:
            for rows in result.partitions():
                table = _rows_to_table(columns, rows)
                if writer is not None:
                    writer.write_table(table.cast(writer.schema))
                    continue
                pending.append(table)
                schema = _unify(pending)
                if any(pa.types.is_null(field.type) for field in schema):
                    continue
                writer = pq.ParquetWriter(output_path, _widen(schema))
                for buffered in pending:
                    writer.write_table(buffered.cast(writer.schema))
                pending = []
        finally:
            if writer is not None:
                writer.close()

    if writer is None:
        # Result ended while some column was still all-NULL (or the result was empty).
        if pending:
            table = pa.concat_tables(pending, promote_options='permissive')
        else:
            table = pa.schema([(column, pa.null()) for column in columns]).empty_table()
        pq.write_table(table, output_path)
