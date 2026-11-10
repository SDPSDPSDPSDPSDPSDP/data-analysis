import pytest

from shirin.plot.svg import Chart, Line, Rect, Text, Wedge, to_svg

from .svg_helpers import svg_attr


def test_rounded_rect_is_pill_shaped() -> None:
    c = Chart(width=6, plot_height=3)
    c.rects.append(Rect(0, 1, 0, 5, '#123456', rounded=True))
    rect = to_svg(c).split('<rect x=')[1]
    assert svg_attr(rect, 'rx') == pytest.approx(min(svg_attr(rect, 'width'), svg_attr(rect, 'height')) / 2)


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


def test_filled_line_draws_fading_area_per_segment() -> None:
    c = Chart(width=6, plot_height=3)
    c.lines += [Line([0, 1, 2, 3], [1, 2, float('nan'), 3], '#123456', fill=True), Line([0, 3], [0, 1], '#654321')]
    svg = to_svg(c)
    assert svg.count('<linearGradient') == 1 and 'stop-opacity="0"' in svg
    area = svg.split('" fill="url(#area')[0].rsplit('<path d="', 1)[1]
    assert area.count('Z') == 2


def test_dark_mode_darkens_background_and_whitens_text_but_keeps_labels_on_bars() -> None:
    c = Chart(width=6, plot_height=3, title='Title')
    c.rects.append(Rect(0, 1, 0, 5, '#ffd5ff'))
    c.texts.append(Text(0.5, 2, 'on bar', '#000000', 10, keep_color=True))
    c.texts.append(Text(0.5, 4, 'beside', '#000000', 10))
    svg = to_svg(c, dark_mode=True)
    assert 'fill="#ffffff"' not in svg
    assert 'fill="#FFFFFF" class="b">Title<' in svg
    assert 'fill="#000000" text-anchor="middle" class="l">on bar<' in svg
    assert 'fill="#FFFFFF" text-anchor="middle" class="l">beside<' in svg


def test_dark_mode_keeps_user_data_colors() -> None:
    c = Chart(width=None, plot_height=3)
    c.x.lim = c.y.lim = (-1.2, 1.2)
    c.x.visible = c.y.visible = False
    c.wedges = [Wedge(0, 0.5, '#ffffff'), Wedge(0.5, 1, '#000000')]
    c.lines.append(Line([0, 1], [0, 1], '#ffffff'))
    c.donut_hole = 0.6
    svg = to_svg(c, dark_mode=True)
    assert 'fill="#ffffff"' in svg and 'fill="#000000"' in svg and 'stroke="#ffffff"' in svg
    assert svg.count('fill="#1e1e1e"') == 2  # background and donut hole
