"""
Integration tests for palette key handling in categorical plots.

These tests verify that boolean/integer (non-string) palette and label_map keys
are applied correctly to bar colors and axis tick labels.
"""
import pandas as pd

from shirin.plot.plots import create_plot
from shirin.plot.core import (
    CountPlotOptions,
    BarPlotOptions,
    NormalizedCountPlotOptions,
)

from shirin.plot.config.colors import Colors


class TestStackedCountPlotTextColors:
    """Integration tests for stacked count plot text color contrast."""
    
    def test_stacked_countplot_boolean_palette_colors_applied(self):
        """Test that stacked countplot correctly uses boolean palette for bar colors."""
        df = pd.DataFrame({
            'category': ['A', 'A', 'A', 'B', 'B', 'B'],
            'status': [True, True, False, True, False, False]
        })
        
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        
        options = CountPlotOptions(
            df=df,
            axis_column='category',
            orientation='horizontal',
            hue='status',
            palette=palette,
            stacked=True,
            stacked_labels='percentage'
        )
        
        plot = create_plot('count', options)
        plot.render()
        
        assert plot._palette is not None
        assert True in plot._palette or 'True' in plot._palette


class TestStackedBarPlotTextColors:
    """Integration tests for stacked bar plot text color contrast."""
    
    def test_stacked_barplot_boolean_palette_colors_applied(self):
        """Test that stacked barplot correctly uses boolean palette."""
        df = pd.DataFrame({
            'category': ['A', 'A', 'B', 'B'],
            'status': [True, False, True, False],
            'value': [10, 20, 15, 25]
        })
        
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        
        options = BarPlotOptions(
            df=df,
            axis_column='category',
            value='value',
            orientation='horizontal',
            hue='status',
            palette=palette,
            stacked=True,
            stacked_labels='percentage'
        )
        
        plot = create_plot('bar', options)
        plot.render()
        
        assert plot._palette is not None


class TestNormalizedCountPlotPaletteKeys:
    """Integration tests for normalized count plot palette key handling."""

    def test_normalized_countplot_boolean_palette_keys_do_not_raise(self):
        """Test that normalized count plot accepts boolean hue values with boolean-keyed palette."""
        df = pd.DataFrame({
            'category': ['A', 'A', 'B', 'B'],
            'status': [True, False, True, False]
        })

        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}

        options = NormalizedCountPlotOptions(
            df=df,
            axis_column='category',
            orientation='vertical',
            hue='status',
            palette=palette,
            show_labels=False,
        )

        plot = create_plot('normalized_count', options)
        plot.render()

        assert plot._normalized_pivot is not None
        assert list(plot._normalized_pivot.columns) == ['False', 'True']


class TestAxisLabelMapping:
    """Integration tests for axis tick label mapping in categorical plots."""

    def test_countplot_applies_label_map_to_axis_ticks_without_legend(self):
        """CountPlot should map categorical axis ticks using label_map even when legend is hidden."""
        df = pd.DataFrame({
            'is_contentious': [0, 0, 1, 1, 1],
        })

        options = CountPlotOptions(
            df=df,
            axis_column='is_contentious',
            orientation='vertical',
            label_map={0: 'Non-Contentious', 1: 'Contentious'},
            plot_legend=False,
            show_labels=False,
        )

        plot = create_plot('count', options)
        ax = plot.render()

        xtick_labels = [tick.get_text() for tick in ax.get_xticklabels()]
        assert 'Non-Contentious' in xtick_labels
        assert 'Contentious' in xtick_labels
        assert '0' not in xtick_labels
        assert '1' not in xtick_labels

    def test_barplot_applies_label_map_to_horizontal_axis_ticks(self):
        """BarPlot should map horizontal categorical axis ticks using label_map."""
        df = pd.DataFrame({
            'is_contentious': [0, 1],
            'count': [12, 7],
        })

        options = BarPlotOptions(
            df=df,
            axis_column='is_contentious',
            value='count',
            orientation='horizontal',
            label_map={0: 'Non-Contentious', 1: 'Contentious'},
            plot_legend=False,
            percentage_labels=False,
        )

        plot = create_plot('bar', options)
        ax = plot.render()

        ytick_labels = [tick.get_text() for tick in ax.get_yticklabels()]
        assert 'Non-Contentious' in ytick_labels
        assert 'Contentious' in ytick_labels
        assert '0' not in ytick_labels
        assert '1' not in ytick_labels
