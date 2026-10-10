"""SQL helpers, run against an in-memory SQLite engine in place of DB2."""
import json
import os
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from shirin.sql import helpers, run_sql_query

CONFIG = {'user': 'u', 'password': 'p@ss:/w', 'host': 'h', 'port': '50000', 'db_name': 'd', 'schema': 'S1'}


@pytest.fixture
def sqlite_engine(monkeypatch):
    engine = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE t (id INTEGER, year INTEGER, note TEXT)'))
        conn.execute(text("INSERT INTO t VALUES (1, 2023, NULL), (2, 2024, NULL), (3, 2024, 'late')"))
    monkeypatch.setattr(helpers, 'get_engine', lambda config: engine)
    return engine


def test_bind_params(sqlite_engine) -> None:
    df = run_sql_query('SELECT id FROM t WHERE year = :year', CONFIG, params={'year': 2024})
    assert df['id'].tolist() == [2, 3]


def test_parquet_chunks_unify_schema(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'out.parquet'
    # chunk_rows=1: 'note' is all-NULL in the first chunks and a string in the last.
    helpers.query_to_parquet('SELECT * FROM t ORDER BY id', CONFIG, out, chunk_rows=1)
    table = pq.read_table(out)
    assert table.num_rows == 3
    assert table.column('note').to_pylist() == [None, None, 'late']


def test_parquet_streams_one_row_group_per_chunk(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'typed.parquet'
    helpers.query_to_parquet('SELECT id, year FROM t ORDER BY id', CONFIG, out, chunk_rows=1)
    parquet = pq.ParquetFile(out)
    assert parquet.metadata.num_row_groups == 3
    assert parquet.read().column('year').to_pylist() == [2023, 2024, 2024]


def test_parquet_all_null_column(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'nulls.parquet'
    helpers.query_to_parquet('SELECT id, note FROM t WHERE note IS NULL', CONFIG, out, chunk_rows=1)
    assert pq.read_table(out).column('note').to_pylist() == [None, None]


def test_parquet_widens_decimals_across_chunks(sqlite_engine, tmp_path, monkeypatch) -> None:
    # SQLite has no DECIMAL type; turn its text into Decimals the way ibm_db returns them.
    monkeypatch.setattr(helpers, '_rows_to_table', lambda columns, rows: pa.Table.from_arrays(
        [pa.array([Decimal(value) for (value,) in rows])], names=columns))
    out = tmp_path / 'decimal.parquet'
    helpers.query_to_parquet("SELECT '1.50' AS v UNION ALL SELECT '12345.75'", CONFIG, out, chunk_rows=1)
    assert pq.read_table(out).column('v').to_pylist() == [Decimal('1.50'), Decimal('12345.75')]


def test_parquet_empty_result(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'empty.parquet'
    run_sql_query('SELECT * FROM t WHERE id < 0', CONFIG, output_path=out)
    assert pq.read_table(out).num_rows == 0


def test_engine_is_cached_and_password_escaped(monkeypatch) -> None:
    # Building a real ibm_db_sa engine loads the DB2 driver DLLs; capture the URL instead.
    urls = []
    monkeypatch.setattr(helpers, 'create_engine', lambda url, **kwargs: urls.append(url) or create_engine('sqlite://'))
    helpers._get_engine.cache_clear()

    first, second = helpers.get_engine(CONFIG), helpers.get_engine(dict(CONFIG))

    assert first is second
    assert len(urls) == 1
    assert urls[0].password == 'p@ss:/w'
    assert urls[0].port == 50000
    helpers._get_engine.cache_clear()


@pytest.mark.parametrize('schema', ['S1; DROP TABLE x', 'a b', '1abc'])
def test_invalid_schema_rejected(schema: str) -> None:
    with pytest.raises(ValueError, match='Invalid schema'):
        helpers.get_engine({**CONFIG, 'schema': schema})


def test_missing_config_keys() -> None:
    with pytest.raises(KeyError, match='schema'):
        helpers.get_engine({k: v for k, v in CONFIG.items() if k != 'schema'})


def test_config_and_query_from_files(sqlite_engine, tmp_path) -> None:
    config_path = tmp_path / 'db.json'
    config_path.write_text(json.dumps(CONFIG))
    sql_path = tmp_path / 'q.sql'
    sql_path.write_text('SELECT COUNT(*) AS n FROM t')
    assert run_sql_query(sql_path, config_path)['n'].tolist() == [3]


@pytest.mark.skipif('DB2_TEST_CONFIG' not in os.environ, reason='set DB2_TEST_CONFIG to a DB2 config JSON path')
def test_db2_integration(tmp_path) -> None:
    """Live DB2: SET SCHEMA hook, ibm_db_sa streaming and bind params."""
    config = Path(os.environ['DB2_TEST_CONFIG'])
    query = 'SELECT CURRENT SCHEMA AS s, CAST(:n AS INTEGER) AS n FROM SYSIBM.SYSDUMMY1'
    df = run_sql_query(query, config, params={'n': 7})
    assert df['n'].tolist() == [7]
    assert df['s'].str.strip().str.upper().tolist() == [helpers.load_db_config(config)['schema'].upper()]
    out = tmp_path / 'db2.parquet'
    run_sql_query(query, config, output_path=out, params={'n': 7})
    assert pq.read_table(out).num_rows == 1
