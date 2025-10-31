import pandas as pd


def print_rounded(name, value):
    print(f"{name}: {value:,.0f}".replace(',', '.'))


@pd.api.extensions.register_series_accessor("stats")
class StatsAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    
    def __call__(self, printing: bool = True):
        stats = {
            'mean': self._obj.mean(),
            'median': self._obj.median(),
            'min': self._obj.min(),
            'max': self._obj.max(),
        }
        
        if printing:
            print_rounded("Mean", stats['mean'])
            print_rounded("Median", stats['median'])
            print_rounded("Minimum", stats['min'])
            print_rounded("Maximum", stats['max'])
            return None
        
        return stats
