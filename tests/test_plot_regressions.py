"""Regressions on single plot classes: what ends up in the rendered Chart."""
import dataclasses

import pandas as pd
import pytest

from shirin.plot.config import Marks, TextColors
from shirin.plot.core import (
    BarPlotOptions,
    CountPlotOptions,
    NormalizedPlotOptions,
    PiePlotOptions,
)
from shirin.plot.plots import BarPlot, CountPlot, NormalizedPlot, PieChart
from shirin.plot.svg import to_svg


def test_countplot_data_labels_false_draws_no_labels(df: pd.DataFrame) -> None:
    rendered = CountPlot(CountPlotOptions(df=df, axis_column='category', data_labels=False))
    chart = rendered.render()
    assert len(chart.texts) == 0


@pytest.mark.parametrize('orientation', ['vertical', 'horizontal'])
def test_bar_charts_have_no_grid_and_soft_labels(df: pd.DataFrame, orientation: str) -> None:
    chart = CountPlot(CountPlotOptions(df=df, axis_column='category', orientation=orientation)).render()
    assert not chart.x.grid and not chart.y.grid
    assert {text.color for text in chart.texts} == {TextColors.FAINT_GREY}

    stacked = CountPlot(CountPlotOptions(df=df, axis_column='category', hue='group', stacked=True)).render()
    assert stacked.texts and all(text.alpha == Marks.INNER_LABEL_ALPHA for text in stacked.texts)

    normalized = NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='category', hue='group', orientation=orientation))
    chart = normalized.render()
    assert not chart.x.grid and not chart.y.grid
    assert 'fill-opacity' in to_svg(chart)


def test_stacked_barplot_sums_duplicate_rows() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'B'], 'hue': ['x', 'x', 'y'], 'v': [1, 2, 3]})
    options = BarPlotOptions(
        df=df, axis_column='cat', value='v', hue='hue', stacked=True,
        palette={'x': '#111111', 'y': '#eeeeee'},
    )
    chart = BarPlot(options).render()
    assert max(rect.height for rect in chart.rects) == 3


def test_stacked_without_dict_palette_raises(df: pd.DataFrame) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', stacked=True, palette='#123456')
    with pytest.raises(ValueError, match="palette must be a dictionary"):
        CountPlot(options).render()


def test_render_does_not_mutate_caller_options(df: pd.DataFrame) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', palette={'x': '#111111', 'y': '#eeeeee'})
    before = dataclasses.replace(options)
    CountPlot(options).render()
    assert options.palette == before.palette
    assert options.label_map is None


@pytest.mark.parametrize("palette", [None, '#123456'])
def test_hue_without_dict_palette_gets_one_color_per_hue_value(df: pd.DataFrame, palette) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', palette=palette)
    rendered = CountPlot(options)
    chart = rendered.render()
    assert rendered._color is None
    assert len(set(rendered._palette.values())) == 2
    assert len({rect.color for rect in chart.rects}) == 2


def test_countplot_counts_per_category_and_hue() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'A', 'B'], 'hue': ['x', 'x', 'y', 'y']})
    chart = CountPlot(CountPlotOptions(df=df, axis_column='cat', hue='hue', palette={'x': '#111111', 'y': '#eeeeee'})).render()
    heights = sorted(rect.height for rect in chart.rects if rect.height > 0)
    assert heights == [1, 1, 2]
    assert chart.x.tick_labels == ['A', 'B']


def test_barplot_sums_per_category() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'B'], 'v': [1.0, 3.0, 5.0]})
    chart = BarPlot(BarPlotOptions(df=df, axis_column='cat', value='v', orientation='horizontal')).render()
    assert sorted(rect.width for rect in chart.rects) == [4.0, 5.0]
    assert chart.y.lim[0] > chart.y.lim[1]  # first category on top


def test_unknown_column_raises_clear_error(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="hue='missing' is not a column"):
        CountPlot(CountPlotOptions(df=df, axis_column='category', hue='missing')).render()


def test_stacked_and_normalized_without_palette_use_default_colors(df: pd.DataFrame) -> None:
    CountPlot(CountPlotOptions(df=df, axis_column='category', hue='group', stacked=True)).render()
    NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='category', hue='group')).render()


def test_missing_palette_key_raises_key_error(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    with pytest.raises(KeyError, match="Palette missing keys"):
        PieChart(PiePlotOptions(df=counts, col='count', palette={'A': '#111111'})).render()


def test_negative_bars_get_labels_below_the_bar() -> None:
    df = pd.DataFrame({'team': ['a', 'b'], 'delta': [5.0, -3.0]})
    chart = BarPlot(BarPlotOptions(df=df, axis_column='team', value='delta')).render()
    labels = {t.text: t for t in chart.texts}
    assert labels['5'].va == 'bottom' and labels['-3'].va == 'top' and labels['-3'].dy < 0
