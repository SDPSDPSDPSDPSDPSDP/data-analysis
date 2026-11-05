import pandas as pd

from shirin.plot.svg.fonts import text_width
from shirin.plot.svg.ticks import date_ticks, nice_ticks, to_days


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


def test_digits_are_tabular() -> None:
    assert text_width('11', 10) == text_width('00', 10)
    assert text_width('11', 10, bold=True) == text_width('00', 10, bold=True)
