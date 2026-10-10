"""Stream a query result into a parquet file without pandas."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text
from sqlalchemy.engine import Connection, CursorResult

from . import engine

PARQUET_CHUNK_ROWS = 100_000


def _execute_streaming(
    connection: Connection, sql_query: str, params: Optional[Dict[str, Any]], chunk_rows: int
) -> CursorResult:
    """Same parsing rules as helpers._read_sql, but rows are fetched chunk_rows at a time."""
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
    with engine.get_engine(db_config).connect() as connection:
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
