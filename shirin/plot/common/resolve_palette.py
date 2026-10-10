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
            sources = (
                ('palette', 'palette', 'Palette', self._palette),
                ('label_map', 'label_mapping', 'LabelMapping', self._label_mapping),
            )
            for arg, name, base, source in sources:
                if a.get(arg) is not None or source is None:
                    continue
                if not callable(getattr(source, 'get', None)):
                    raise TypeError(f"{name} must be a {base} subclass, got {type(source).__name__}")
                a[arg] = source.get(column)

        return method(*bound.args, **bound.kwargs)

    return wrapper
