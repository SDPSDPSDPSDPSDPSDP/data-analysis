import pytest

from shirin.plot.svg import Chart, Rect, Text, to_svg

from .svg_helpers import svg_attr


def test_long_data_label_shrinks_plot_width() -> None:
    def bar_width(label: str) -> float:
        c = Chart(width=6, plot_height=1)
        c.rects.append(Rect(0, 10, 0, 1, '#123456'))
        c.texts.append(Text(10, 0.5, label, '#000000', 8, 'left'))
        bar = to_svg(c).split('fill="#123456"')[0].rsplit('<rect', 1)[1]
        return svg_attr(bar, 'width')

    assert bar_width('a' * 40) < bar_width('a')


def test_value_ticks_lighter_than_category_ticks() -> None:
    c = Chart(width=4, plot_height=2)
    c.x.lim, c.y.lim = (0, 10), (-0.5, 0.5)
    c.y.ticks, c.y.tick_labels = [0], ['Apple']
    c.x.ticks = [5]
    svg = to_svg(c)
    assert 'fill="#444444"' in svg.split('>Apple<')[0][-80:]
    assert 'fill="#777777"' in svg.split('>5<')[0][-80:]


def test_categorical_tick_label_map_requires_tick_labels() -> None:
    from shirin.plot.common.formatting import format_categorical_tick_labels

    with pytest.raises(ValueError, match="no tick labels"):
        format_categorical_tick_labels(Chart(width=1, plot_height=1), {'a': 'A'}, axis='x')


def test_crowded_data_labels_get_shortened() -> None:
    def chart(gap: float) -> Chart:
        c = Chart(width=3, plot_height=3)
        c.x.lim = (0, 10)
        for i in range(2):
            c.rects.append(Rect(i * gap, i * gap + 0.1, 0, 5, '#123456'))
            c.texts.append(Text(i * gap + 0.05, 5, '10.915', '#000000', 8, 'center', 'bottom', short_text='11k'))
        return c
    crowded = chart(0.5)
    assert '>11k<' in to_svg(crowded)
    assert [t.text for t in crowded.texts] == ['10.915', '10.915']
    assert '>11k<' in to_svg(crowded)
    assert '>10.915<' in to_svg(chart(5))


def test_crowded_x_ticks_get_shortened_then_thinned() -> None:
    from shirin.number_format import format_compact, format_thousands

    def chart(width: float, hi: float) -> str:
        c = Chart(width=width, plot_height=2)
        c.x.lim = (0, hi)
        c.x.formatter, c.x.short_formatter = format_thousands, format_compact
        c.rects.append(Rect(0, hi, 0, 1, '#123456'))
        return to_svg(c)

    assert '>2.000.000<' in chart(8, 2_000_000)
    narrow = chart(3, 2_000_000)
    assert '>500k<' in narrow and '>500.000<' not in narrow
    tiny = chart(1.5, 2_000_000)
    assert '>1M<' in tiny and '>500k<' not in tiny
