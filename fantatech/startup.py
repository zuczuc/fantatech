from .data_loaders.combine import load_data
from .visualization import stats
from . import formations
from .team_builder.builder import Team, CURRENT_YEAR

df, player = load_data()

def show_players_stats(player_ids, years=None, nrows=None):
    stats.show_players_stats(df, player_ids, years=years, nrows=nrows)

def build_team(player_ids, target_formations=None):
    Team(df, player_ids, target_formations=target_formations).display()