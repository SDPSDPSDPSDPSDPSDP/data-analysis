from typing import Any


def is_all_numeric(values: list) -> tuple[bool, list[float]]:
    numeric_values = []
    for v in values:
        try:
            numeric_values.append(float(str(v)))
        except (ValueError, TypeError):
            return False, []
    return True, numeric_values


def sort_alphabetically(values: Any, ascending: bool = True) -> list:
    values_list = list(values)
    is_numeric, numeric_vals = is_all_numeric(values_list)
    
    if is_numeric:
        sorted_pairs = sorted(zip(numeric_vals, values_list), key=lambda x: x[0], reverse=not ascending)
        return [original_val for _, original_val in sorted_pairs]
    else:
        return sorted(values_list, reverse=not ascending)
