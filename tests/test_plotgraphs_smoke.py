"""Smoke tests: every public PlotGraphs method renders without raising, plus regressions."""
import dataclasses
from typing import List

import pandas as pd
import pytest

from shirin.plot import PlotGraphs
from shirin.plot.common.colors import blend
from shirin.plot.config import FigureSize
from shirin.plot.config.colors import REMAINDER_TINT
from shirin.plot.common.data_conversion import REMAINDER_SHARE_COL, fill_missing_values_in_data, fill_remainder
from shirin.plot.core import (
    BarPlotOptions,
    CountPlotOptions,
    HistogramOptions,
    NormalizedPlotOptions,
    PiePlotOptions,
)
from shirin.plot.plots import BarPlot, CountPlot, Histogram, NormalizedPlot, PieChart


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


GROUP_PALETTE = {'group': {'x': '#111111', 'y': '#eeeeee'}}
GROUP_LABELS = {'group': {'x': 'Ex'}}


def test_every_method_renders(df: pd.DataFrame, shown: List[str]) -> None:
    plot = PlotGraphs(palette=GROUP_PALETTE)
    plot.bar(df, x='category')
    plot.bar(df, y='category', hue='group', stacked=True)
    plot.bar(df, x='category', hue='group', normalized=True)
    plot.bar(df, x='category', value='value')
    plot.bar(df, y='category', value='value', hue='group', stacked=True)
    plot.histogram(df, x='value')
    plot.lineplot(df, x='date', y='value', hue='group')
    plot.scatterplot(df, x='value', y='value')
    plot.pie(df, col='category')
    plot.timeplot(df, x='date', group_by='month')
    plot.timeplot(df, x='date', group_by='day', plot_type='line', rotation=45)
    assert len(shown) == 11
    assert all(svg.startswith('<svg') for svg in shown)


def test_countplot_data_labels_false_draws_no_labels(df: pd.DataFrame) -> None:
    rendered = CountPlot(CountPlotOptions(df=df, axis_column='category', data_labels=False))
    chart = rendered.render()
    assert len(chart.texts) == 0


def test_pie_without_palette_uses_distinct_colors(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    chart = PieChart(PiePlotOptions(df=counts, col='count')).render()
    assert len({wedge.color for wedge in chart.wedges}) == 3


def test_histogram_keeps_fractional_values() -> None:
    df = pd.DataFrame({'x': [0.1, 0.2, 0.5, 0.9, None]})
    chart = Histogram(HistogramOptions(df=df, x='x', bins=10)).render()
    assert len(chart.rects) == 10
    assert sum(rect.height for rect in chart.rects) == 4


def test_histogram_suffix_on_tick_labels() -> None:
    df = pd.DataFrame({'x': [0.5, 1.5, 2.5]})
    chart = Histogram(HistogramOptions(df=df, x='x', bins=3, suffix='%')).render()
    assert chart.x.formatter(10) == '10 %'


def test_histogram_bars_round_and_stacks_clip_to_total() -> None:
    df = pd.DataFrame({'x': [1, 1, 2, 3], 'hue': ['a', 'b', 'a', 'b']})
    plain = Histogram(HistogramOptions(df=df, x='x', bins=3)).render()
    assert all(rect.rounded and rect.clip is None for rect in plain.rects)
    palette = {'a': '#111111', 'b': '#eeeeee'}
    stacked = Histogram(HistogramOptions(df=df, x='x', bins=3, hue='hue', palette=palette)).render()
    assert all(not rect.rounded and rect.clip.rounded for rect in stacked.rects)
    assert stacked.rects[0].clip.height == 2
    assert stacked.rects[0].fade_to == '#eeeeee'
    assert stacked.rects[1].fade_to is None


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


def test_title_and_mapped_legend_render(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs(font='satoshi', label_mapping=GROUP_LABELS).bar(
        df, x='category', hue='group', title='Totals', legend=True
    )
    assert '>Totals</text>' in shown[0]
    assert '>Ex</text>' in shown[0]
    assert '@font-face' in shown[0]


def test_hidden_legend(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().bar(df, x='category', hue='group')
    assert '>x</text>' not in shown[0]


def test_bad_palette_config_raises() -> None:
    with pytest.raises(TypeError, match="palette must be a dict"):
        PlotGraphs(palette=['#111111'])
    with pytest.raises(TypeError, match=r"label_mapping\['group'\] must be a dict"):
        PlotGraphs(label_mapping={'group': 'Ex'})


def test_unknown_font_raises() -> None:
    with pytest.raises(ValueError, match="Unknown font"):
        PlotGraphs(font='comic sans')


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


def test_pie_on_column_named_count(plot: PlotGraphs) -> None:
    plot.pie(pd.DataFrame({'count': ['a', 'b', 'b']}), col='count')


def test_shift_fill_interpolates_in_x_order() -> None:
    df = pd.DataFrame({'x': [3, 1, 2], 'y': [30.0, 10.0, None]})
    filled = fill_missing_values_in_data(df, 'x', 'y', hue=None, fill_method='shift')
    assert filled.set_index('x').loc[2, 'y'] == 20.0


def test_title_list_adds_subtitle(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().bar(df, x='category', title=['Totals', 'Per category'])
    assert '>Totals</text>' in shown[0]
    assert '>Per category</text>' in shown[0]
    with pytest.raises(ValueError, match='title must be'):
        PlotGraphs().bar(df, x='category', title=['a', 'b', 'c'])


def test_countplot_direction_from_x_or_y(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().bar(df, y='category')
    PlotGraphs().bar(df, y='category', x_axis_label='')
    assert '>Count</text>' in shown[0]
    assert '>Count</text>' not in shown[1]
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df, x='category', y='category')
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df)


def test_barplot_needs_exactly_one_of_x_or_y(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df, x='category', y='category', value='value')
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df, value='value')


def test_bar_rejects_options_of_the_other_mode(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match='remainder needs value'):
        PlotGraphs().bar(df, x='category', normalized=True, remainder=True)
    with pytest.raises(ValueError, match='top_n only works without value'):
        PlotGraphs().bar(df, x='category', value='value', top_n=2)


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


def test_normalized_barplot_hue_equal_to_axis_draws_full_width_share_bars() -> None:
    df = pd.DataFrame({'fruit': ['a', 'b'], 'count': [3, 1]})
    plot = BarPlot(BarPlotOptions(df=df, axis_column='fruit', value='count', hue='fruit', normalized=True))
    plot.render()
    assert {round(rect.x1 - rect.x0, 3) for rect in plot.chart.rects} == {FigureSize.BAR_GROUP_WIDTH}
    assert sorted(text.text for text in plot.chart.texts) == ['25.0%', '75.0%']
