from IPython.display import display
import copy
import pandas as pd
import matplotlib.pyplot as plt

from ..constants import CURRENT_YEAR
from ..analysis.stats import get_players_stats, get_players_summaries
from ..analysis.aggregators import aggregate_players_stats


def show_players_stats(df, player_ids, years=None, nrows=None):
    summaries = get_players_summaries(df, player_ids)
    stats = aggregate_players_stats(df, player_ids, years=years)

    multi_year = not isinstance(years, int)
    if not multi_year:
        stats = stats.sort_values(f'Fv*', ascending=False)
    if len(summaries) > 1 and multi_year:
        stats = stats[['Fv*']]

    # Format stats cols
    cols_formats = {}
    for c in ['GP%', 'Rf%']:
        cols_formats[c] = '{:.1%}'
    for c in ['quantileOrder']:
        cols_formats[c] = '{:.0%}'
    for c in ['FvTot', 'FvTotExtra', 'Quotazione']:
        cols_formats[c] = '{:.1f}'
    for c in ['V', 'Fv', 'Fv*', 'VStd', 'FvStd', 'FvExtra'] + [c for c in summaries.columns if 'Fv' in c]:
        cols_formats[c] = '{:.2f}'
    for c in ['G', 'Gf', 'Rf', 'Ass', 'Asf', 'Amm', 'Esp', 'Au', 'Gs', 'Rp']:
        cols_formats[c] = '{:.0f}'
    if nrows is not None:
        stats = stats.iloc[:nrows - 1]
    stats = stats.style.format(cols_formats)

    cmap = copy.copy(plt.cm.get_cmap('RdYlGn'))

    if len(summaries) > 1:
        summaries = summaries.sort_values(f'Fv* ({CURRENT_YEAR - 1})', ascending=False)
        if nrows is not None:
            summaries = summaries.iloc[:nrows - 1]

        summaries = (
            summaries.style
                .background_gradient(cmap, subset=[c for c in summaries.columns if 'Fv' in c], axis=None)
                .background_gradient('Blues', subset=['quantileOrder'], axis=None)
                .format(cols_formats)
                .highlight_null('lightgray')
        )

        if not isinstance(years, int):
            stats = stats.background_gradient(cmap, axis=None).format('{:.2f}').highlight_null('lightgray')


    display(summaries)
    display(stats)

def color_nan_white(x):
    color = 'white' if pd.isnull(x) else 'black'
    return 'color: %s' % color