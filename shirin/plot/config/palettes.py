from typing import Any, Dict, Union

from .colors import Colors


class Palette:
    """Base class for defining per-column palettes.

    Built-in palettes (``good_bad``, ``good_bad_dark``) are ready to use directly
    or as a starting point when subclassing.

    Subclass this and add class-level dicts where each attribute name is a
    column name used as ``hue`` (or ``x``/``col``) in plot calls.

    Example::

        class MyPalettes(Palette):
            category: dict = {"A": "#57ccff", "B": "#e3c2ff"}
            is_correct: dict = Palette.is_correct

        plot = PlotGraphs(palette=MyPalettes, label_mapping=MyLabels)

    Per-call ``palette=`` / ``label_map=`` arguments always take priority over
    the class-level defaults.
    """

    is_correct: Dict[Any, str] = {
        True:  Colors.GOOD_GREEN,
        False: Colors.BAD_RED,
    }

    @classmethod
    def get(cls, column: str) -> Union[Dict[Any, str], str, None]:
        return vars(cls).get(column)


class LabelMapping:
    """Base class for per-column label mappings.

    Same structure as :class:`Palette` — each attribute name is a column name.

    Example::

        class MyLabels(LabelMapping):
            is_correct: dict = {True: "Good", False: "Bad"}
    """

    is_correct: Dict[Any, str] = {
        True:  'Correct',
        False: 'Incorrect',
    }

    @classmethod
    def get(cls, column: str) -> Union[Dict[Any, str], None]:
        return vars(cls).get(column)
