import pandas as pd

from ..constants import CURRENT_YEAR


def aggregate_stats(df, by):
    years = df['Season'].unique()

    agg = {
        'Week': ['min', 'max', 'count'],
        'Voto_Fantacalcio': ['mean', 'std'],
        'Fv': ['sum', 'mean', 'std'],
        'BonusMalus': ['mean', 'std'],
        'Gf': 'sum',
        'Gs': 'sum',
        'Au': 'sum',
        'Rf': 'sum',
        'Rp': 'sum',
        'Rs': 'sum',
        'Ass': 'sum',
        'Asf': 'sum',
        'Amm': 'sum',
        'Esp': 'sum',
    }

    cols = [
        'From', 'To', 'GP', 'V', 'VStd', 'FvTot', 'Fv', 'FvStd', 'BM', 'BMStd',
        'Gf', 'Gs', 'Au', 'Rf', 'Rp', 'Rs', 'Ass', 'Asf', 'Amm', 'Esp',
    ]

    if 'FvSub' in df.columns:
        agg['FvSub'] = 'first'
        cols.append('FvSub')
    if 'FvTotSub' in df.columns:
        agg['FvTotSub'] = 'first'
        cols.append('FvTotSub')
    if 'Cost' in df.columns:
        agg['Cost'] = 'first'
        cols.append('Cost')

    # Aggregate
    df = df.groupby(by).agg(agg)
    df.columns = cols

    # Compute additional stats
    df['BM'] = df['Fv'] - df['V']
    df['G'] = df['To'] - df['From'] + 1
    # How to identify players that arrived in January?
    # How to deal with current season
    num_games = pd.Series(38, index=df.index)
    if 'Season' in df.index.names:
        num_games = num_games.mask(df.index.get_level_values('Season') == CURRENT_YEAR , 4)
    if len(years) == 1 and years[0] == CURRENT_YEAR:
        num_games = 4

    df['GP%'] = df['GP'] / num_games
    df['Rf%'] = df['Rf'] / (df['Rf'] + df['Rs'])
    if 'FvSub' in df.columns:
        df['FvExtra'] = df['Fv'] - df['FvSub']
        df['Fv*'] = df['Fv'] * df['GP%'] + df['FvSub'] * (1 - df['GP%'])  # Fv corrected for games not played, when the sub plays
    if 'FvTotSub' in df.columns:
        df['FvTotExtra'] = df['FvTot'] - df['FvTotSub']

    return df




def aggregate_players_stats(df, player_ids=None, years=None, multiplayer=None):
    from .stats import get_players_stats

    stats = get_players_stats(df, player_ids, years=years)

    stats['Nome'] = stats['Nome'].str.title()
    multi_player = stats['Nome'].nunique() > 1 if multiplayer is None else multiplayer
    multi_year = stats['Season'].nunique() > 1

    by = []
    by.append('Season')
    stats['Season'] = stats['Season'].astype(int)
    if multi_player:
        by.append('Nome')
    else:
        by.append('Team')

    stats = aggregate_stats(stats, by)

    if multi_player:
        if multi_year:
            stats = stats.unstack('Nome')
        else:
            stats = stats.reset_index('Season', drop=True)
    else:
        stats = stats.reset_index().set_index(['Season', 'To', 'Team']).sort_index().reset_index('To', drop=True)

    return stats[[c for c in [
        'Fv', 'Fv*', 'FvExtra',
        # 'FvTot', 'FvTotExtra',
        'GP%', 'V', 'Gf', 'Rf', 'Rf%',
        'Ass', 'Asf',
        'Amm', 'Esp', 'Au',
        'Gs', 'Rp',
        # 'VStd', 'FvStd',
    ] if c in stats.columns]]

