import pandas as pd

from ..number_format import format_thousands

_PRINTED = (('Mean', 'mean'), ('Median', 'median'), ('Minimum', 'min'), ('Maximum', 'max'))


@pd.api.extensions.register_series_accessor("stats")
class StatsAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, printing: bool = True):
        missing_values = int(self._obj.isna().sum())
        stats = {
            'mean': self._obj.mean(),
            'median': self._obj.median(),
            'min': self._obj.min(),
            'max': self._obj.max(),
            'missing_values': missing_values,
        }
        if not printing:
            return stats

        for label, key in _PRINTED:
            print(f"{label}: {format_thousands(stats[key])}")
        if missing_values > 0:
            print(f"\nMissing Values: {format_thousands(missing_values)}")
        return None
