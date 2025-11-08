import pandas as pd
import pytest
from shirin.plot.common.sorting import (
    sort_alphabetically,
    sort_by_frequency,
    create_colors_list,
)


def test_sort_alphabetically_strings():
    """Test alphabetical sorting with strings."""
    values = ['zebra', 'apple', 'banana']
    result = sort_alphabetically(values, ascending=True)
    assert result == ['apple', 'banana', 'zebra']


def test_sort_alphabetically_numeric_strings():
    """Test numeric-aware sorting."""
    values = ['10', '2', '1', '20']
    result = sort_alphabetically(values, ascending=True)
    assert result == ['1', '2', '10', '20']


def test_sort_alphabetically_descending():
    """Test descending alphabetical sort."""
    values = ['a', 'b', 'c']
    result = sort_alphabetically(values, ascending=False)
    assert result == ['c', 'b', 'a']


def test_sort_by_frequency():
    """Test frequency-based sorting."""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [10, 20, 30],
        'C': [5, 5, 5]
    })
    
    result = sort_by_frequency(df, ascending=False)
    
    # B should be first (sum=60), then C (sum=15), then A (sum=6)
    # The function sorts by sum, so index 2 (B=60), index 1 (B=20), index 0 (B=10)
    assert list(result.index) == [2, 1, 0]
    assert 'A' in result.columns
    assert '_order' not in result.columns  # Should be removed


def test_create_colors_list():
    """Test creating color list from palette."""
    df = pd.DataFrame({
        'red': [1, 2],
        'blue': [3, 4]
    })
    palette = {'red': '#FF0000', 'blue': '#0000FF'}
    
    result = create_colors_list(df, palette)
    
    assert result == ['#FF0000', '#0000FF']
