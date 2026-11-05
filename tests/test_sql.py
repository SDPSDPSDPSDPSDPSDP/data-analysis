"""SQL helpers, run against an in-memory SQLite engine in place of DB2."""
import json
import os
from pathlib import Path

import pyarrow.parquet as pq
import pytest
from sqlalchemy import create_engine

from shirin.sql import Database, engine

from .conftest import CREDENTIALS


def test_bind_params(db) -> None:
    df = db.sql('SELECT id FROM t WHERE year = :year', params={'year': 2024})
    assert df['id'].tolist() == [2, 3]


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
