import pandas as pd

from .aggregators import aggregate_players_stats

def compare_player_stats(df, player_id_1, player_id_2, years=None):
    stats_1 = aggregate_players_stats(df, player_id_1, years=years)
    stats_2 = aggregate_players_stats(df, player_id_2, years=years)
    stats = pd.merge(stats_1, stats_2, how='outer', on='Season', suffixes=('_1', '_2'))

    # Compute deltas
    for c in stats_1.columns:
        stats[f'd{c}'] = stats[f'{c}_2'] - stats[f'{c}_1']

    return stats
