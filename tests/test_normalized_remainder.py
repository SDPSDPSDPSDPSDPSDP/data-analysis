"""Normalized bars and the remainder option (fractions filled up to one)."""
import pandas as pd
import pytest

from shirin.plot import PlotGraphs
from shirin.plot.common.colors import blend
from shirin.plot.common.data_conversion import REMAINDER_SHARE_COL, fill_remainder
from shirin.plot.config import FigureSize
from shirin.plot.config.colors import REMAINDER_TINT
from shirin.plot.core import BarPlotOptions, NormalizedPlotOptions
from shirin.plot.plots import BarPlot, NormalizedPlot


def test_normalized_barplot_shares_summed_value_per_hue() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'A'], 'hue': ['x', 'x', 'y'], 'v': [1, 2, 1]})
    plot = NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='cat', hue='hue', value='v'))
    plot.render()
    assert plot._normalized_pivot.loc['A'].tolist() == [0.75, 0.25]


def test_normalized_barplot_accepts_duplicate_index() -> None:
    df = pd.DataFrame({'cat': ['A', 'A'], 'hue': ['x', 'y'], 'v': [3, 1]}, index=[0, 0])
    plot = NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='cat', hue='hue', value='v'))
    plot.render()
    assert plot._normalized_pivot.loc['A'].tolist() == [0.75, 0.25]


def test_barplot_remainder_fills_to_one_sorted_by_fraction(plot: PlotGraphs) -> None:
    df = pd.DataFrame({'run': ['a', 'b'], 'acc': [0.7, 0.9]})
    plot.bar(df, x='run', value='acc', normalized=True, remainder=True)
    shares = fill_remainder(df, 'run', 'acc', 'Incorrect')
    plot_obj = NormalizedPlot(NormalizedPlotOptions(df=shares, axis_column='run', hue='acc', value=REMAINDER_SHARE_COL, remainder='Incorrect'))
    plot_obj.render()
    assert plot_obj._normalized_pivot.columns.tolist() == ['acc', 'Incorrect']
    assert plot_obj._normalized_pivot.index.tolist() == ['b', 'a']


def test_barplot_remainder_rejects_non_fractions(plot: PlotGraphs) -> None:
    with pytest.raises(ValueError, match=r"fractions in \[0, 1\]"):
        plot.bar(pd.DataFrame({'run': ['a'], 'acc': [78]}), x='run', value='acc', normalized=True, remainder=True)


def test_two_level_normalized_draws_first_pill_over_full_second() -> None:
    df = pd.DataFrame({'run': ['a', 'a'], 'acc': ['acc', 'Incorrect'], 'v': [0.7, 0.3]})
    plot = NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='run', hue='acc', value='v', remainder='Incorrect'))
    chart = plot.draw(plot.transform(plot.preprocess()))
    back, front = chart.rects
    assert (back.y0, back.y1, front.y0, front.y1) == (0, 1, 0, 0.7)
    assert back.rounded and front.rounded and back.fade_to is None
    assert back.color == blend(front.color, '#FFFFFF', REMAINDER_TINT)


def test_barplot_remainder_rejects_conflicting_fractions(plot: PlotGraphs) -> None:
    with pytest.raises(ValueError, match='same on every row'):
        plot.bar(pd.DataFrame({'run': ['a', 'a'], 'acc': [0.5, 0.6]}), x='run', value='acc', normalized=True, remainder=True)


def test_fill_remainder_collapses_repeated_fraction() -> None:
    df = pd.DataFrame({'run': ['a', 'a', 'b'], 'acc': [0.6, 0.6, 0.9]})
    filled = fill_remainder(df, 'run', 'acc', 'Incorrect')
    assert filled[REMAINDER_SHARE_COL].round(2).tolist() == [0.6, 0.9, 0.4, 0.1]


def test_remainder_segment_has_no_data_label() -> None:
    df = pd.DataFrame({'run': ['a', 'a'], 'acc': ['acc', 'Incorrect'], 'v': [0.7, 0.3]})
    plot = NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='run', hue='acc', value='v', remainder='Incorrect'))
    chart = plot.draw(plot.transform(plot.preprocess()))
    plot.format_plot(chart)
    assert [text.text for text in chart.texts] == ['70%']


def test_barplot_remainder_with_category_hue_colors_each_bar(plot: PlotGraphs) -> None:
    df = pd.DataFrame({'run': ['a', 'b'], 'acc': [0.7, 0.9]})
    options = NormalizedPlotOptions(
        df=fill_remainder(df, 'run', 'acc', 'Incorrect'), axis_column='run', hue='acc', value=REMAINDER_SHARE_COL,
        remainder='Incorrect', category_palette={'a': '#ff0000', 'b': '#0000ff'},
    )
    nplot = NormalizedPlot(options)
    chart = nplot.draw(nplot.transform(nplot.preprocess()))
    fronts = [rect.color for rect in chart.rects[1::2]]
    assert fronts == ['#0000ff', '#ff0000']
    plot.bar(df, y='run', value='acc', hue='run', remainder=True, normalized=True)


def test_barplot_remainder_rejects_other_hue(plot: PlotGraphs) -> None:
    df = pd.DataFrame({'run': ['a'], 'acc': [0.7], 'g': ['x']})
    with pytest.raises(ValueError, match='hue must be the category column'):
        plot.bar(df, x='run', value='acc', hue='g', remainder=True, normalized=True)


def test_remainder_not_in_legend() -> None:
    df = pd.DataFrame({'run': ['a', 'a'], 'acc': ['acc', 'Incorrect'], 'v': [0.7, 0.3]})
    plot = NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='run', hue='acc', value='v', remainder='Incorrect', legend=True))
    plot.render()
    assert [label for _, label, _ in plot.chart.legend] == ['acc']


def test_remainder_legend_keeps_level_labelled_like_remainder() -> None:
    df = pd.DataFrame({'run': ['a', 'a'], 'acc': ['acc', 'Incorrect'], 'v': [0.7, 0.3]})
    plot = NormalizedPlot(NormalizedPlotOptions(
        df=df, axis_column='run', hue='acc', value='v', remainder='Incorrect', legend=True, label_map={'acc': 'Incorrect'},
    ))
    plot.render()
    assert [label for _, label, _ in plot.chart.legend] == ['Incorrect']


def test_normalized_barplot_hue_equal_to_axis_draws_full_width_share_bars() -> None:
    df = pd.DataFrame({'fruit': ['a', 'b'], 'count': [3, 1]})
    plot = BarPlot(BarPlotOptions(df=df, axis_column='fruit', value='count', hue='fruit', normalized=True))
    plot.render()
    assert {round(rect.x1 - rect.x0, 3) for rect in plot.chart.rects} == {FigureSize.BAR_GROUP_WIDTH}
    assert sorted(text.text for text in plot.chart.texts) == ['25,0%', '75,0%']


def test_dark_mode_remainder_tints_toward_dark_background(shown: list) -> None:
    df = pd.DataFrame({'run': ['a'], 'acc': [0.7]})
    PlotGraphs(dark_mode=True, palette={'run': {'a': '#ff0000'}}).bar(
        df, y='run', value='acc', hue='run', remainder=True, normalized=True,
    )
    assert f'fill="{blend("#ff0000", "#1e1e1e", REMAINDER_TINT)}"' in shown[0]
    assert f'fill="{blend("#ff0000", "#ffffff", REMAINDER_TINT)}"' not in shown[0]
