from shirin.stats.number_format import format_thousands


def test_format_thousands_for_int():
    assert format_thousands(1234567) == "1.234.567"


def test_format_thousands_for_float():
    assert format_thousands(1234.56) == "1.235"
