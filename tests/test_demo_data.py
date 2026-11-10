import pytest

from shirin.assets import data


def test_threshold_curve_marks_are_thresholds() -> None:
    df = data.df_threshold_curve

    marked = df.dropna(subset=['marked'])
    assert list(marked['marked']) == [0.5, 0.8, 0.9, 0.95]
    assert (marked['marked'] == marked['threshold']).all()
    assert df['coverage'].is_monotonic_decreasing


def test_unknown_demo_frame_raises() -> None:
    with pytest.raises(AttributeError, match='df_missing'):
        _ = data.df_missing
