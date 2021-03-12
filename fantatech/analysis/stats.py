import numpy as np

from .prototype_substitutes import get_prototype_substites
from ..constants import CURRENT_YEAR
from .fv_quantiles import enrich_with_fv_quantiles_by_role

def get_players_stats(df, player_ids=None, years=None):
    subs = get_prototype_substites(df)
    mask = np.full(len(df), True)
    if player_ids is not None:
        mask &= df['Id'].isin(_listify_player_ids(player_ids))
    if years is not None:
        if isinstance(years, int):
            years = [years]
        mask &= df['Season'].isin(years)
    df = df.loc[mask].copy()
    df = df.join(subs, how='left', on='Ruolo')
    return df

def get_players_summaries(df, player_ids):
    from .aggregators import aggregate_players_stats

    stats = get_players_stats(df, player_ids)
    agg = aggregate_players_stats(df, player_ids)

    summaries = stats.groupby('Nome').last()[[
        'Ruolo',
        'RuoloMantra',
        'Team',
        'QuotazioneAttuale'
    ]].rename(columns={
        'RuoloMantra': 'Mantra',
        'Team': 'Squadra',
        'QuotazioneAttuale': 'Quotazione',
    })

    summaries.index = summaries.index.str.title()
    summaries['Squadra'] = summaries['Squadra'].str.title()
    summaries['Quotazione'] *= 4 / 5

    for year_offset in range(-3, 0):
        try:
            if 'Team' in agg.index.names:
                summaries[f'Fv* ({CURRENT_YEAR + year_offset})'] = np.round(agg.loc[CURRENT_YEAR + year_offset, 'Fv*'].iloc[0], decimals=2)
            else:
                summaries[f'Fv* ({CURRENT_YEAR + year_offset})'] = np.round(agg.loc[CURRENT_YEAR + year_offset, 'Fv*'], decimals=2)
        except KeyError:
            summaries[f'Fv* ({CURRENT_YEAR + year_offset})'] = np.nan

    try:
        summaries = enrich_with_fv_quantiles_by_role(df, summaries, col=f'Fv* ({CURRENT_YEAR - 1})')
    except ValueError:
        pass

    return summaries


def _listify_player_ids(player_ids):
    if isinstance(player_ids, int):
        return [player_ids]
    return player_ids