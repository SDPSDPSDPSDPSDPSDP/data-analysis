"""
Tests for data conversion utilities, specifically boolean label_map fix
"""
from shirin.plot.common.data_conversion import convert_dict_keys_to_string


def test_convert_dict_keys_boolean():
    """Test that boolean keys are converted to strings"""
    
    # Test with boolean keys
    label_map = {True: "Good", False: "Bad"}
    palette = {True: "#00FF00", False: "#FF0000"}
    
    converted_label_map = convert_dict_keys_to_string(label_map)
    converted_palette = convert_dict_keys_to_string(palette)
    
    # Check that keys are now strings
    assert "True" in converted_label_map, "True key should be converted to string 'True'"
    assert "False" in converted_label_map, "False key should be converted to string 'False'"
    assert "True" in converted_palette, "Palette True key should be converted to string"
    assert "False" in converted_palette, "Palette False key should be converted to string"
    
    # Check that values are preserved
    assert converted_label_map["True"] == "Good", "Label value should be preserved"
    assert converted_label_map["False"] == "Bad", "Label value should be preserved"
    assert converted_palette["True"] == "#00FF00", "Palette color should be preserved"
    assert converted_palette["False"] == "#FF0000", "Palette color should be preserved"


def test_convert_dict_keys_none():
    """Test that None values are handled correctly"""
    
    converted_label_map = convert_dict_keys_to_string(None)
    converted_palette = convert_dict_keys_to_string(None)
    
    assert converted_label_map is None, "None label_map should remain None"
    assert converted_palette is None, "None palette should remain None"


def test_convert_dict_keys_string():
    """Test that string keys remain unchanged"""
    
    label_map = {"cat1": "Category 1", "cat2": "Category 2"}
    
    converted_label_map = convert_dict_keys_to_string(label_map)
    
    assert "cat1" in converted_label_map, "String key should remain as string"
    assert converted_label_map["cat1"] == "Category 1", "Value should be preserved"


def test_convert_dict_keys_integer():
    """Test that integer keys are converted to strings"""
    
    label_map = {1: "One", 2: "Two", 3: "Three"}
    palette = {1: "#FF0000", 2: "#00FF00", 3: "#0000FF"}
    
    converted_label_map = convert_dict_keys_to_string(label_map)
    converted_palette = convert_dict_keys_to_string(palette)
    
    assert "1" in converted_label_map, "Integer keys should be converted to strings"
    assert "2" in converted_palette, "Palette integer keys should be converted"
    assert converted_label_map["1"] == "One", "Values should be preserved"


def test_convert_dict_keys_mixed():
    """Test that mixed key types are all converted to strings"""
    
    mixed_dict = {
        True: "Boolean True",
        2: "Integer Two",
        "key": "String Key",
        2.5: "Float Value"
    }
    
    converted = convert_dict_keys_to_string(mixed_dict)
    
    assert "True" in converted, "Boolean key should be converted"
    assert "2" in converted, "Integer key should be converted"
    assert "key" in converted, "String key should remain"
    assert "2.5" in converted, "Float key should be converted"
    assert converted["True"] == "Boolean True", "Values should be preserved"
