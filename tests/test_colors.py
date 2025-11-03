from shirin.plot.config.colors import Colors, TextColors


def test_colors_exist():
    """Test that color constants are defined."""
    assert Colors.BLACK == '#000000'
    assert Colors.RED == '#A52B5A'
    assert Colors.GREEN == '#dcffee'


def test_text_colors_exist():
    """Test that text color constants are defined."""
    assert TextColors.BLACK == '#000000'
    assert TextColors.WHITE == '#FFFFFF'
    assert TextColors.DARK_GREY == '#444444'


def test_colors_are_hex():
    """Test that colors are valid hex format."""
    assert Colors.GREY.startswith('#')
    assert len(Colors.GREY) == 7  # #RRGGBB format
