import pandas as pd

from .number_format import format_thousands


def print_rounded(name, value):
    print(f"{name}: {format_thousands(value)}")



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
        
        if printing:
            print_rounded("Mean", stats['mean'])
            print_rounded("Median", stats['median'])
            print_rounded("Minimum", stats['min'])
            print_rounded("Maximum", stats['max'])
            if missing_values > 0:
                print(f"\nMissing Values: {format_thousands(missing_values)}")
            return None
        
        return stats
