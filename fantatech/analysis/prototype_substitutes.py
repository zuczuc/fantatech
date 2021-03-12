from .aggregators import aggregate_stats
from ..constants import CURRENT_YEAR


def get_prototype_substites(df, min_gp_pct=0.4, max_gp_pct=0.7):
    agg_players = aggregate_stats(df.loc[df['Season'] == CURRENT_YEAR - 1], ['Nome', 'Ruolo'])
    agg_players = agg_players.loc[agg_players['GP%'].between(min_gp_pct, max_gp_pct)]
    return agg_players.groupby(level='Ruolo')[['Fv', 'FvTot']].median().rename(columns={'Fv': 'FvSub', 'FvTot': 'FvTotSub'})