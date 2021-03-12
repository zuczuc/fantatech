import pandas as pd

from . import players
from . import stats

def load_data(list_type=players.ListType.MANTRA):

    df_players = players.load_players_list(list_type)
    df_stats = stats.load_players_stats()

    player = players.create_player_class(df_players)

    # Keep votes only for players still playing in serie A
    df = pd.merge(
        df_players,
        df_stats[df_stats.columns.difference(['Nome'])],
        how='left',
        on='Id',
    )

    return df, player