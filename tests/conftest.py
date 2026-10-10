from typing import List

import pandas as pd
import pytest

import shirin.plot.all_plots as all_plots
from shirin.plot import PlotGraphs


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

