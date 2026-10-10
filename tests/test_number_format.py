from shirin.number_format import format_thousands


def test_format_thousands_for_int():
    assert format_thousands(1234567) == "1.234.567"


def test_format_thousands_for_float():
    assert format_thousands(1234.56) == "1.235"


def test_format_thousands_keeps_small_decimals():
    assert format_thousands(1.25) == "1,25"
    assert format_thousands(0.5) == "0,5"
    assert format_thousands(3.0) == "3"
