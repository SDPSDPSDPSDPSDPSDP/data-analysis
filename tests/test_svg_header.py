import pytest

from shirin.plot.svg import Chart, Rect, to_svg
from shirin.plot.svg.fonts import text_width

from .svg_helpers import svg_attr


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

    assert svg_attr(to_svg(chart('Title')), 'height') > svg_attr(to_svg(chart('')), 'height')


def test_title_gets_extra_top_gap() -> None:
    from shirin.plot.config import Layout
    from shirin.plot.svg.header import header_rows

    _, plot_top = header_rows(Chart(width=6, plot_height=3, title='T'), 100, str)
    assert plot_top == Layout.PAD + Layout.TITLE_TOP_GAP + 15 + Layout.PLOT_GAP


def test_title_is_centered_on_image() -> None:
    def title_center(title: str) -> float:
        c = Chart(width=6, plot_height=3, title=title)
        c.y.label = 'Count'
        c.rects.append(Rect(0, 1, 0, 50000, '#123456'))
        shift = float(to_svg(c).split('translate(')[1].split(' ')[0])
        return shift + text_width(title, 15, bold=True) / 2

    # translate() is written with 2 decimals.
    assert title_center('T') == pytest.approx(6 * 72 / 2, abs=0.01)
    assert title_center('A much longer title') == pytest.approx(6 * 72 / 2, abs=0.01)


def test_legend_value_drawn_lighter_after_label() -> None:
    c = Chart(None, plot_height=2)
    c.x.lim = c.y.lim = (-1, 1)
    c.legend = [('#ff0000', 'Apple', '9.027')]
    svg = to_svg(c)
    assert 'fill="#444444">Apple<' in svg
    assert 'fill="#c4c4c4">9.027<' in svg
