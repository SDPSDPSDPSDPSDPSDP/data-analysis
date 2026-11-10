import pytest

from shirin.assets import data


def test_threshold_curve_marks_are_thresholds() -> None:
    df = data.df_threshold_curve

    assert list(df.loc[df['marked'], 'threshold']) == [0.5, 0.8, 0.9, 0.95]
    assert df['coverage'].is_monotonic_decreasing


def test_threshold_curve_accuracy_rises_smoothly() -> None:
    assert data.df_threshold_curve['accuracy'].is_monotonic_increasing


def test_unknown_demo_frame_raises() -> None:
    with pytest.raises(AttributeError, match='df_missing'):
        _ = data.df_missing


def test_threshold_curves_has_one_curve_per_detector() -> None:
    df = data.df_threshold_curves

    assert set(df['detector']) == {'Old detector', 'New detector'}
    for _, curve in df.groupby('detector'):
        assert curve['accuracy'].is_monotonic_increasing
        assert list(curve.loc[curve['marked'], 'threshold']) == [0.5, 0.8, 0.9, 0.95]


def test_new_detector_is_more_accurate() -> None:
    accuracy = data.df_threshold_curves.groupby('detector')['accuracy'].mean()

    assert accuracy['New detector'] > accuracy['Old detector']
