# %% [setup]
from shirin.number_format import format_compact, format_percentage, format_thousands

# %% Thousands
format_thousands(1234567)
format_thousands(1234.5678, decimals=2)

# %% Percentage
format_percentage(12.5, decimals=1)

# %% Compact
format_compact(1517)
format_compact(10915)
format_compact(2400000)
