"""Unit tests for palette conversion with non-string keys (boolean, integer)."""
from shirin.plot.common.data_conversion import convert_palette_to_strings
from shirin.plot.common.formatting.text_contrast import get_text_color_for_background
from shirin.plot.config.colors import Colors, TextColors


class TestPaletteLookupWithBooleanKeys:
    """Tests for palette color lookup with boolean keys (regression tests)."""
    
    def test_boolean_palette_converted_to_strings(self):
        """Test that boolean palette keys are correctly converted to strings."""
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        palette_str = convert_palette_to_strings(palette)
        
        assert 'True' in palette_str
        assert 'False' in palette_str
        assert palette_str['True'] == Colors.BAD_RED
        assert palette_str['False'] == Colors.GOOD_GREEN
    
    def test_text_color_lookup_with_string_converted_palette(self):
        """Test that text colors are correctly determined after string conversion."""
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        palette_str = convert_palette_to_strings(palette)
        
        # Simulate what happens in stacked plots - lookup by string key
        bg_color_true = palette_str.get('True', '#000000')
        bg_color_false = palette_str.get('False', '#000000')
        
        # BAD_RED is dark -> white text
        assert get_text_color_for_background(bg_color_true) == TextColors.WHITE
        # GOOD_GREEN is light -> black text
        assert get_text_color_for_background(bg_color_false) == TextColors.BLACK
    
    def test_direct_color_list_lookup(self):
        """Test that using pre-computed colors list works correctly (pie chart fix)."""
        # Simulate pie chart scenario where _colors is already computed
        colors = [Colors.BAD_RED, Colors.GOOD_GREEN]
        
        text_colors = [get_text_color_for_background(c) for c in colors]
        
        assert text_colors[0] == TextColors.WHITE  # BAD_RED -> white text
        assert text_colors[1] == TextColors.BLACK  # GOOD_GREEN -> black text
    
    def test_failed_lookup_returns_black_background(self):
        """Test that failed palette lookup defaults to black (white text)."""
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        
        # This simulates the bug - looking up string key in boolean-keyed dict
        bg_color = palette.get('True', '#000000')  # Will return default black
        
        # This is why we needed the fix - wrong lookup gives black background
        assert bg_color == '#000000'
        assert get_text_color_for_background(bg_color) == TextColors.WHITE


class TestPaletteLookupWithIntegerKeys:
    """Tests for palette color lookup with integer keys."""
    
    def test_integer_palette_converted_to_strings(self):
        """Test that integer palette keys are correctly converted to strings."""
        palette = {1: Colors.BAD_RED, 2: Colors.GOOD_GREEN}
        palette_str = convert_palette_to_strings(palette)
        
        assert '1' in palette_str
        assert '2' in palette_str
        assert palette_str['1'] == Colors.BAD_RED
        assert palette_str['2'] == Colors.GOOD_GREEN
    
    def test_text_color_lookup_with_integer_converted_palette(self):
        """Test that text colors are correctly determined after integer key conversion."""
        palette = {1: Colors.BAD_RED, 2: Colors.GOOD_GREEN}
        palette_str = convert_palette_to_strings(palette)
        
        bg_color_1 = palette_str.get('1', '#000000')
        bg_color_2 = palette_str.get('2', '#000000')
        
        assert get_text_color_for_background(bg_color_1) == TextColors.WHITE
        assert get_text_color_for_background(bg_color_2) == TextColors.BLACK
