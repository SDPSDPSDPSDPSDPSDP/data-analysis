from typing import List

import pytest

import shirin.plot.all_plots as all_plots


@pytest.fixture(autouse=True)
def shown(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """Collect the SVGs PlotGraphs would display instead of needing a notebook."""
    svgs: List[str] = []
    monkeypatch.setattr(all_plots, 'show', svgs.append)
    return svgs
