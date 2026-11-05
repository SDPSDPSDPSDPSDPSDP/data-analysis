import struct
from typing import List

import pytest

import shirin.plot.all_plots as all_plots
from shirin.plot.config import FigureSize
from shirin.plot.svg import to_png


def _png_size(png: bytes) -> tuple:
    assert png[:8] == b'\x89PNG\r\n\x1a\n'
    return struct.unpack('>II', png[16:24])


def test_show_sends_svg_and_png_in_one_bundle(monkeypatch: pytest.MonkeyPatch, df, shown: List[str]) -> None:
    all_plots.PlotGraphs().bar(df, x='category')
    svg = shown[0]
    monkeypatch.undo()

    displayed = []
    monkeypatch.setattr('IPython.display.display', lambda obj, raw: displayed.append((obj, raw)))
    all_plots.show(svg)

    (bundle, raw), = displayed
    assert raw is True
    assert bundle['image/svg+xml'] == svg
    _png_size(bundle['image/png'])


def test_png_is_scaled_svg_size(df, shown: List[str]) -> None:
    all_plots.PlotGraphs().bar(df, x='category')
    svg = shown[0]
    width = int(svg.split('width="', 1)[1].split('"', 1)[0])
    height = int(svg.split('height="', 1)[1].split('"', 1)[0])

    assert _png_size(to_png(svg)) == (width * FigureSize.PNG_SCALE, height * FigureSize.PNG_SCALE)
