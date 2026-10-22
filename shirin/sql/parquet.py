"""Stream a query result into a parquet file without pandas."""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text
from sqlalchemy.engine import Connection, CursorResult, Engine

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


def _widen(schema: pa.Schema) -> pa.Schema:
    """Arrow infers decimal precision per chunk; widen to the max so later chunks still fit."""
    return pa.schema([
        field.with_type(pa.decimal128(38, field.type.scale)) if pa.types.is_decimal(field.type) else field
        for field in schema
    ])


def _spill(table: pa.Table, spill_dir: Path, index: int) -> Path:
    path = spill_dir / f'{index}.parquet'
    pq.write_table(table, path)
    return path


def _drain(writer: pq.ParquetWriter, spilled: List[Path]) -> None:
    """Copy spilled chunks into writer one at a time, deleting each once written."""
    for path in spilled:
        writer.write_table(pq.read_table(path).cast(writer.schema))
        path.unlink()
    spilled.clear()


def _stream_to_parquet(
    sql_query: str,
    engine: Engine,
    output_path: Path,
    params: Optional[Dict[str, Any]],
    chunk_rows: int,
) -> None:
    """Stream the result into one parquet file, chunk_rows rows at a time, without pandas.

    The parquet schema is fixed once every column has a real type. Until then chunks are
    spilled to temporary parquet files next to output_path, so memory stays at one chunk
    even when a column is NULL for millions of leading rows.
    """
    with engine.connect() as connection, tempfile.TemporaryDirectory(dir=output_path.parent) as spill_dir:
        result = _execute_streaming(connection, sql_query, params, chunk_rows)
        columns = list(result.keys())
        schema = pa.schema([(column, pa.null()) for column in columns])
        spilled: List[Path] = []
        writer: Optional[pq.ParquetWriter] = None
        try:
            for index, rows in enumerate(result.partitions()):
                table = _rows_to_table(columns, rows)
                if writer is not None:
                    writer.write_table(table.cast(writer.schema))
                    continue
                spilled.append(_spill(table, Path(spill_dir), index))
                schema = pa.unify_schemas([schema, table.schema], promote_options='permissive')
                if any(pa.types.is_null(field.type) for field in schema):
                    continue
                writer = pq.ParquetWriter(output_path, _widen(schema))
                _drain(writer, spilled)
            if writer is None:
                # Result ended while some column was still all-NULL (or the result was empty).
                writer = pq.ParquetWriter(output_path, _widen(schema))
                _drain(writer, spilled)
        finally:
            if writer is not None:
                writer.close()


def query_to_parquet(
    sql_query: str,
    engine: Engine,
    output_path: Path,
    params: Optional[Dict[str, Any]] = None,
    chunk_rows: int = PARQUET_CHUNK_ROWS,
) -> None:
    """Write to a .part file first, so a failed query never leaves a truncated parquet at output_path."""
    output_path = Path(output_path)
    part_path = output_path.with_name(output_path.name + '.part')
    try:
        _stream_to_parquet(sql_query, engine, part_path, params, chunk_rows)
    except BaseException:
        part_path.unlink(missing_ok=True)
        raise
    os.replace(part_path, output_path)
