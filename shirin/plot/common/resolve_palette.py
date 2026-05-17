import functools
import inspect


def resolve_palette(method):
    """Injects palette and label_map from the PlotGraphs instance defaults.

    Reads ``hue`` or ``col`` from the call arguments and fills in ``palette``
    and ``label_map`` when they are absent, using the class-level ``_palette``
    and ``_label_mapping`` registered on the instance.
    """
    sig = inspect.signature(method)

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        bound = sig.bind(self, *args, **kwargs)
        bound.apply_defaults()
        a = bound.arguments

        column = a.get('hue') or a.get('col')
        if column is not None:
            if a.get('palette') is None and self._palette is not None:
                a['palette'] = self._palette.get(column)
            if a.get('label_map') is None and self._label_mapping is not None:
                a['label_map'] = self._label_mapping.get(column)

        return method(*bound.args, **bound.kwargs)

    return wrapper
