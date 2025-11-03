import pandas as pd
from shirin.stats.descriptive_statistics import StatsAccessor  # Import to register the accessor


def test_stats_accessor_calculation():
    """Test stats accessor calculates correct values."""
    series = pd.Series([1, 2, 3, 4, 5])
    
    result = series.stats(printing=False)
    
    assert result['mean'] == 3.0
    assert result['median'] == 3.0
    assert result['min'] == 1
    assert result['max'] == 5
    assert result['missing_values'] == 0


def test_stats_accessor_with_missing():
    """Test stats accessor handles missing values."""
    series = pd.Series([1, 2, None, 4, 5])
    
    result = series.stats(printing=False)
    
    assert result['mean'] == 3.0  # (1+2+4+5)/4
    assert result['missing_values'] == 1


def test_stats_accessor_printing(capsys):
    """Test stats accessor prints output when requested."""
    series = pd.Series([10, 20, 30])
    
    result = series.stats(printing=True)
    
    assert result is None  # Should return None when printing
    
    captured = capsys.readouterr()
    assert 'Mean: 20' in captured.out
    assert 'Median: 20' in captured.out
