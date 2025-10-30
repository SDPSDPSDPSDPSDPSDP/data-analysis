import pandas as pd

def print_rounded(name, value):
    print(f"{name}: {value:,.0f}".replace(',', '.'))

def print_stats(df: pd.DataFrame, column: str, printing: bool=True):

    stats = {
        'mean': df[column].mean(),
        'median': df[column].median(),
        'min': df[column].min(),
        'max': df[column].max(),
    }
    
    if printing:
        print_rounded("Mean", stats['mean'])
        print_rounded("Median", stats['median'])
        print_rounded("Minimum", stats['min'])
        print_rounded("Maximum", stats['max'])