import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def close_plots():
    """Close all matplotlib figures after each test."""
    yield
    plt.close('all')
