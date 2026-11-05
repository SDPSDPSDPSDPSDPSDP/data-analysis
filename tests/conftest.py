from typing import List

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

import shirin.plot.all_plots as all_plots
from shirin.plot import PlotGraphs
from shirin.sql import Database, engine

CREDENTIALS = {'user': 'u', 'password': 'p@ss:/w', 'host': 'h', 'port': '50000', 'db_name': 'd', 'schema': 'S1'}


@pytest.fixture(autouse=True)
def shown(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """Collect the SVGs PlotGraphs would display instead of needing a notebook."""
    svgs: List[str] = []
    monkeypatch.setattr(all_plots, 'show', svgs.append)
    return svgs


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame({
        'category': ['A', 'A', 'B', 'B', 'C', 'C'],
        'group': ['x', 'y', 'x', 'y', 'x', 'x'],
        'value': [1.5, 2.0, 3.0, 4.0, 5.0, 0.5],
        'date': pd.date_range('2023-01-01', periods=6, freq='35D'),
    })


@pytest.fixture
def plot() -> PlotGraphs:
    return PlotGraphs()


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
