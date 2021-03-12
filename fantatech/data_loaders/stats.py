import os
import pandas as pd

from ..constants import ROOT_DIR

FILEPATH_STATS = os.path.join(ROOT_DIR, 'data/processed/voti.csv')


def load_players_stats():
    df = pd.read_csv(FILEPATH_STATS).rename(columns={
        'Fantacalcio_id': 'Id',
    }).drop([
        'Voto_Italia',
        'sv_Italia',
        'Voto_Statistico',
        'sv_Statistico',
    ], axis=1).astype({
        'Season': int, 
        'Week': int, 
    })

    # Enrichment
    df['Team'] = df['Team'].str.title()
    
    df['Fv'] = (
        df.Voto_Fantacalcio + 
        3 * df.Gf
        -1 * df.Gs 
        - 2 * df.Au 
        + 3 * df.Rf
        + 3 * df.Rp
        - 3 * df.Rs
        + 1 * df.Ass 
        + 1 * df.Asf
        - 0.5 * df.Amm
        - 1 * df.Esp
    )

    df['BonusMalus'] = df['Fv'] - df['Voto_Fantacalcio']

    return df