import enum
import os
import pandas as pd

from ..constants import ROOT_DIR

class ListType(enum.Enum):
    CLASSIC = 'CLASSIC'
    MANTRA = 'MANTRA'

FILEPATH_PLAYERS_LIST_CLASSIC = os.path.join(ROOT_DIR, 'data/processed/lista_classic.csv')
FILEPATH_PLAYERS_LIST_MANTRA = os.path.join(ROOT_DIR, 'data/processed/lista_mantra.csv')


def load_players_list(list_type=ListType.MANTRA):
    filepath = FILEPATH_PLAYERS_LIST_CLASSIC if list_type is ListType.CLASSIC else FILEPATH_PLAYERS_LIST_MANTRA
    filepath = os.path.abspath(filepath)
    df = pd.read_csv(filepath).rename(columns={
        'R': 'RuoloMantra',
        'Qt. A': 'QuotazioneAttuale',
        'Qt. I': 'QuotazioneIniziale',
        'Diff.': 'DiffQuotazione'
    })

    # Enrichment
    df['NomeStd'] = standardize_players_names(df['Nome'])

    return df


def standardize_players_names(x):
    return x.str.normalize('NFKD')\
            .str.encode('ascii', errors='ignore')\
            .str.decode('utf-8')\
            .str.replace(' ', '_')\
            .str.replace('.', '')\
            .str.replace("'", '')\
            .str.replace("-", '_')


def create_player_class(df):
    class Player(object):
        pass
    player = Player()
    for x in df.itertuples():
        setattr(player, x.NomeStd, x.Id)
        setattr(player, x.NomeStd.lower(), x.Id)
    return player