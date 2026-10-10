from shirin.number_format import format_compact, format_thousands


def test_format_thousands_for_int():
    assert format_thousands(1234567) == "1.234.567"


def test_format_thousands_for_float():
    assert format_thousands(1234.56) == "1.235"


def test_format_thousands_keeps_small_decimals():
    assert format_thousands(1.25) == "1,25"
    assert format_thousands(0.5) == "0,5"
    assert format_thousands(3.0) == "3"


def test_format_compact() -> None:
    assert format_compact(10915) == "11k"
    assert format_compact(1517) == "1,5k"
    assert format_compact(7000) == "7k"
    assert format_compact(2_500_000) == "2,5M"
    assert format_compact(950) == "950"
