import pandas as pd
import pytest

from shirin.plot.svg import Chart, Rect, Text, Wedge, to_svg
from shirin.plot.svg.fonts import text_width
from shirin.plot.svg.ticks import date_ticks, nice_ticks, to_days


def _attr(svg: str, name: str) -> float:
    return float(svg.split(f'{name}="')[1].split('"')[0])


def test_nice_ticks() -> None:
    assert nice_ticks(0, 105) == [0, 25, 50, 75, 100]
    assert nice_ticks(0, 1.05) == [0, 0.25, 0.5, 0.75, 1.0]
    assert nice_ticks(-3, 3) == [-2, 0, 2]
    assert nice_ticks(5, 5) == [5]


def test_date_ticks_pick_coarser_steps_for_long_ranges() -> None:
    days = to_days(pd.Series(pd.to_datetime(['2023-01-01', '2023-06-15', '2040-01-01'])))
    _, labels = date_ticks(days[0], days[1])
    assert labels[0] == 'Jan 2023' and len(labels) <= 8
    _, labels = date_ticks(days[0], days[2])
    assert labels[0] == '2023' and len(labels) <= 8


def test_text_width_grows_with_text() -> None:
    assert 0 < text_width('1', 10) < text_width('1000', 10) < text_width('1000', 20)


def test_subtitle_is_tracked_tighter_than_small_text() -> None:
    assert text_width('Share', 10) / 10 < text_width('Share', 8) / 8
    c = Chart(width=6, plot_height=3, subtitle='Share')
    c.rects.append(Rect(0, 1, 0, 5, '#123456'))
    assert 'class="l">Share<' in to_svg(c)


def test_title_adds_height_instead_of_squeezing_plot() -> None:
    def chart(title: str) -> Chart:
        c = Chart(width=6, plot_height=3, title=title)
        c.rects.append(Rect(0, 1, 0, 5, '#123456'))
        return c

    assert _attr(to_svg(chart('Title')), 'height') > _attr(to_svg(chart('')), 'height')


def test_title_is_centered_over_plot() -> None:
    def title_center(title: str) -> float:
        c = Chart(width=6, plot_height=3, title=title)
        c.rects.append(Rect(0, 1, 0, 5, '#123456'))
        shift = float(to_svg(c).split('translate(')[1].split(' ')[0])
        return shift + text_width(title, 15, bold=True) / 2

    assert title_center('T') == pytest.approx(title_center('A much longer title'))


def test_rounded_rect_is_pill_shaped() -> None:
    c = Chart(width=6, plot_height=3)
    c.rects.append(Rect(0, 1, 0, 5, '#123456', rounded=True))
    rect = to_svg(c).split('<rect x=')[1]
    assert _attr(rect, 'rx') == pytest.approx(min(_attr(rect, 'width'), _attr(rect, 'height')) / 2)


def test_stacked_segments_share_one_clip_path() -> None:
    c = Chart(width=6, plot_height=3)
    outline = Rect(0, 1, 0, 5, '', rounded=True)
    c.rects += [Rect(0, 1, 0, 2, '#111111', clip=outline), Rect(0, 1, 2, 5, '#222222', clip=outline)]
    svg = to_svg(c)
    assert svg.count('<clipPath') == 1 and svg.count('clip-path="url(#') == 2


def test_stacked_segment_fades_into_next_inside_clip() -> None:
    c = Chart(width=6, plot_height=3)
    outline = Rect(0, 1, 0, 5, '', rounded=True)
    c.rects += [Rect(0, 1, 0, 2, '#111111', clip=outline, fade_to='#222222'), Rect(0, 1, 2, 5, '#222222', clip=outline)]
    svg = to_svg(c)
    assert svg.count('<linearGradient') == 1 and 'stop-color="#222222"' in svg
    assert svg.count('clip-path="url(#') == 3


def test_long_data_label_shrinks_plot_width() -> None:
    def bar_width(label: str) -> float:
        c = Chart(width=6, plot_height=1)
        c.rects.append(Rect(0, 10, 0, 1, '#123456'))
        c.texts.append(Text(10, 0.5, label, '#000000', 8, 'left'))
        bar = to_svg(c).split('fill="#123456"')[0].rsplit('<rect', 1)[1]
        return _attr(bar, 'width')

    assert bar_width('a' * 40) < bar_width('a')


def test_axis_without_data_raises() -> None:
    with pytest.raises(ValueError, match="no data"):
        to_svg(Chart(width=6, plot_height=3))


def test_wedge_stroked_in_own_color_hides_seams() -> None:
    c = Chart(None, plot_height=2)
    c.x.lim = c.y.lim = (-1, 1)
    c.wedges = [Wedge(0, 0.3, '#ff0000'), Wedge(0.3, 1, '#00ff00')]
    svg = to_svg(c)
    assert 'fill="#ff0000" stroke="#ff0000"' in svg
    assert 'fill="#00ff00" stroke="#00ff00"' in svg


def test_legend_value_drawn_lighter_after_label() -> None:
    c = Chart(None, plot_height=2)
    c.x.lim = c.y.lim = (-1, 1)
    c.legend = [('#ff0000', 'Apple', '9.027')]
    svg = to_svg(c)
    assert 'fill="#444444">Apple<' in svg
    assert 'fill="#aaaaaa">9.027<' in svg


def test_categorical_tick_label_map_requires_tick_labels() -> None:
    from shirin.plot.common.formatting import format_categorical_tick_labels

    with pytest.raises(ValueError, match="no tick labels"):
        format_categorical_tick_labels(Chart(width=1, plot_height=1), {'a': 'A'}, axis='x')
