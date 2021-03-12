import numpy as np
import pandas as pd

from .aggregators import aggregate_stats
from ..constants import CURRENT_YEAR


def get_fv_quantiles_by_role(df):
    stats = aggregate_stats(df.loc[df['Season'] == CURRENT_YEAR - 1], ['Id', 'Ruolo'])
    stats = stats.loc[(stats['GP%'] >= 0.3) & (stats['GP'] > 10)]
    return stats.groupby(level='Ruolo')['Fv'].quantile(np.linspace(0, 1, 101)).rename_axis(['Ruolo', 'quantileOrder']).rename('quantileFv').reset_index()


def enrich_with_fv_quantiles_by_role(df, df_to_enrich, col='Fv'):
    quantiles = get_fv_quantiles_by_role(df).sort_values('quantileFv')
    df_to_enrich['_Fv'] = df_to_enrich[col].fillna(df_to_enrich[col].min())
    index_cols = df_to_enrich.index.names
    df_to_enrich = df_to_enrich.reset_index()
    return pd.merge_asof(df_to_enrich.sort_values('_Fv'), quantiles, left_on='_Fv', right_on='quantileFv', by='Ruolo').drop('_Fv', axis=1).drop('quantileFv', axis=1).set_index(index_cols)

