"""query_to_parquet, run against an in-memory SQLite engine in place of DB2."""
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from sqlalchemy.exc import OperationalError

from shirin.sql import parquet, row_groups


def test_parquet_chunks_unify_schema(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'out.parquet'
    # chunk_rows=1: 'note' is all-NULL in the first chunks and a string in the last.
    parquet.query_to_parquet('SELECT * FROM t ORDER BY id', sqlite_engine, out, chunk_rows=1)
    table = pq.read_table(out)
    assert table.num_rows == 3
    assert table.column('note').to_pylist() == [None, None, 'late']


def test_parquet_spills_untyped_chunks_to_disk(sqlite_engine, tmp_path, monkeypatch) -> None:
    spilled_rows = []
    spill = parquet._spill
    monkeypatch.setattr(parquet, '_spill', lambda table, *args: spilled_rows.append(table.num_rows) or spill(table, *args))
    out = tmp_path / 'out.parquet'
    parquet.query_to_parquet('SELECT * FROM t ORDER BY id', sqlite_engine, out, chunk_rows=1)
    assert spilled_rows == [1, 1, 1]
    assert [path.name for path in tmp_path.iterdir()] == ['out.parquet']
    assert pq.read_table(out).column('note').to_pylist() == [None, None, 'late']


def test_parquet_buffers_chunks_into_row_groups(sqlite_engine, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(row_groups, 'PARQUET_ROW_GROUP_ROWS', 2)
    out = tmp_path / 'typed.parquet'
    parquet.query_to_parquet('SELECT id, year FROM t ORDER BY id', sqlite_engine, out, chunk_rows=1)
    parquet_file = pq.ParquetFile(out)
    assert [parquet_file.metadata.row_group(i).num_rows for i in range(parquet_file.metadata.num_row_groups)] == [2, 1]
    assert parquet_file.read().column('year').to_pylist() == [2023, 2024, 2024]


def test_parquet_reports_progress(sqlite_engine, tmp_path, capsys) -> None:
    parquet.query_to_parquet('SELECT * FROM t', sqlite_engine, tmp_path / 'out.parquet', chunk_rows=1)
    assert 'Fetching: 3 rows' in capsys.readouterr().err


def test_parquet_all_null_column(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'nulls.parquet'
    parquet.query_to_parquet('SELECT id, note FROM t WHERE note IS NULL', sqlite_engine, out, chunk_rows=1)
    assert pq.read_table(out).column('note').to_pylist() == [None, None]


def test_parquet_widens_decimals_across_chunks(sqlite_engine, tmp_path, monkeypatch) -> None:
    # SQLite has no DECIMAL type; turn its text into Decimals the way ibm_db returns them.
    monkeypatch.setattr(parquet, '_rows_to_table', lambda columns, rows: pa.Table.from_arrays(
        [pa.array([Decimal(value) for (value,) in rows])], names=columns))
    out = tmp_path / 'decimal.parquet'
    parquet.query_to_parquet("SELECT '1.50' AS v UNION ALL SELECT '12345.75'", sqlite_engine, out, chunk_rows=1)
    assert pq.read_table(out).column('v').to_pylist() == [Decimal('1.50'), Decimal('12345.75')]


def test_parquet_empty_result(db, tmp_path) -> None:
    out = tmp_path / 'empty.parquet'
    assert db.sql('SELECT * FROM t WHERE id < 0', output_path=out) is None
    assert pq.read_table(out).num_rows == 0


def test_parquet_failed_query_keeps_existing_file(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'out.parquet'
    out.write_bytes(b'previous')
    with pytest.raises(OperationalError):
        parquet.query_to_parquet('SELECT * FROM missing_table', sqlite_engine, out)
    assert out.read_bytes() == b'previous'
    assert list(tmp_path.iterdir()) == [out]
