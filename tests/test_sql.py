"""SQL helpers, run against an in-memory SQLite engine in place of DB2."""
import json
import os
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import StaticPool

from shirin.sql import Database, engine, parquet

CREDENTIALS = {'user': 'u', 'password': 'p@ss:/w', 'host': 'h', 'port': '50000', 'db_name': 'd', 'schema': 'S1'}


@pytest.fixture
def sqlite_engine(monkeypatch):
    sqlite = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
    with sqlite.begin() as conn:
        conn.execute(text('CREATE TABLE t (id INTEGER, year INTEGER, note TEXT)'))
        conn.execute(text("INSERT INTO t VALUES (1, 2023, NULL), (2, 2024, NULL), (3, 2024, 'late')"))
    monkeypatch.setattr(engine, 'get_engine', lambda **credentials: sqlite)
    return sqlite


@pytest.fixture
def db(sqlite_engine) -> Database:
    return Database(**CREDENTIALS)


def test_bind_params(db) -> None:
    df = db.sql('SELECT id FROM t WHERE year = :year', params={'year': 2024})
    assert df['id'].tolist() == [2, 3]


def test_parquet_chunks_unify_schema(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'out.parquet'
    # chunk_rows=1: 'note' is all-NULL in the first chunks and a string in the last.
    parquet.query_to_parquet('SELECT * FROM t ORDER BY id', sqlite_engine, out, chunk_rows=1)
    table = pq.read_table(out)
    assert table.num_rows == 3
    assert table.column('note').to_pylist() == [None, None, 'late']


def test_parquet_streams_one_row_group_per_chunk(sqlite_engine, tmp_path) -> None:
    out = tmp_path / 'typed.parquet'
    parquet.query_to_parquet('SELECT id, year FROM t ORDER BY id', sqlite_engine, out, chunk_rows=1)
    parquet_file = pq.ParquetFile(out)
    assert parquet_file.metadata.num_row_groups == 3
    assert parquet_file.read().column('year').to_pylist() == [2023, 2024, 2024]


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


def test_engine_is_cached_and_password_escaped(monkeypatch) -> None:
    # Building a real ibm_db_sa engine loads the DB2 driver DLLs; capture the URL instead.
    urls = []
    monkeypatch.setattr(engine, 'create_engine', lambda url, **kwargs: urls.append(url) or create_engine('sqlite://'))
    engine._get_engine.cache_clear()

    first, second = Database(**CREDENTIALS), Database(**CREDENTIALS)

    assert first._engine is second._engine
    assert len(urls) == 1
    assert urls[0].password == 'p@ss:/w'
    assert urls[0].port == 50000
    engine._get_engine.cache_clear()


@pytest.mark.parametrize('schema', ['S1; DROP TABLE x', 'a b', '1abc'])
def test_invalid_schema_rejected(schema: str) -> None:
    with pytest.raises(ValueError, match='Invalid schema'):
        Database(**{**CREDENTIALS, 'schema': schema})


def test_query_from_file(db, tmp_path) -> None:
    sql_path = tmp_path / 'q.sql'
    sql_path.write_text('SELECT COUNT(*) AS n FROM t')
    assert db.sql(sql_path)['n'].tolist() == [3]


@pytest.mark.skipif('DB2_TEST_CONFIG' not in os.environ, reason='set DB2_TEST_CONFIG to a JSON file with Database kwargs')
def test_db2_integration(tmp_path) -> None:
    """Live DB2: SET SCHEMA hook, ibm_db_sa streaming and bind params."""
    credentials = json.loads(Path(os.environ['DB2_TEST_CONFIG']).read_text(encoding='utf-8'))
    db = Database(**credentials)
    query = 'SELECT CURRENT SCHEMA AS s, CAST(:n AS INTEGER) AS n FROM SYSIBM.SYSDUMMY1'
    df = db.sql(query, params={'n': 7})
    assert df['n'].tolist() == [7]
    assert df['s'].str.strip().str.upper().tolist() == [credentials['schema'].upper()]
    out = tmp_path / 'db2.parquet'
    db.sql(query, params={'n': 7}, output_path=out)
    assert pq.read_table(out).num_rows == 1


def test_credentials_from_dotenv(monkeypatch, tmp_path) -> None:
    captured = {}
    monkeypatch.setattr(engine, 'get_engine', lambda **credentials: captured.update(credentials))
    for name in CREDENTIALS:
        monkeypatch.delenv(f'DB2_{name.upper()}', raising=False)
    (tmp_path / '.env').write_text('\n'.join(f'DB2_{k.upper()}={v}' for k, v in CREDENTIALS.items()))
    monkeypatch.chdir(tmp_path)

    Database(user='override')

    assert captured == {**CREDENTIALS, 'user': 'override'}
    for name in CREDENTIALS:
        monkeypatch.delenv(f'DB2_{name.upper()}', raising=False)


def test_missing_credentials(monkeypatch, tmp_path) -> None:
    for name in CREDENTIALS:
        monkeypatch.delenv(f'DB2_{name.upper()}', raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match='DB2_SCHEMA'):
        Database(**{k: v for k, v in CREDENTIALS.items() if k != 'schema'})
