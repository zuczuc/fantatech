# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 19:24:51 2020

@author: zuk-8
"""


from collections import OrderedDict
import numpy as np
import pandas as pd


VOTO_TYPE = 'Voto_Italia'



def get_bonus(row, penalty=True):
    goals = 3*row['Gf'] - row['Gs'] - 2*row['Au']
    penalties = 3*row['Rp'] - 3*row['Rs'] + 3*row['Rf']
    assists = row['Ass'] + row['Asf']
    malus = - 0.5*row['Amm'] - row['Esp']
    if penalty is True:
        return goals + penalties + assists + malus
    elif penalty is False:
        return goals + assists + malus
    else:
        raise ValueError("penalty must be either True or False")
        return None


def get_bonus_nop(row):
    return get_bonus(row, penalty=False)


def compute_score(raw_stats, expected_games=None, replacement_score=None):
    if expected_games is None:
        expected_games = sum([GAMES_PS.loc[season, 'Week'] for season in raw_stats['Season'].unique()])
    if replacement_score is None:
        role = raw_stats.groupby('Ruolo')['Week'].count().sort_values(ascending=False).index[0]
        replacement_score = REPLACEMENT_PER_ROLE[role]
    games_played = len(raw_stats.index)
    if games_played > expected_games:
        raise ValueError(f"games_played ({games_played}) > expected_games ({expected_games})")
    sum_grades = raw_stats[[VOTO_TYPE,'Bonus_nop']].sum(1)
    return ((sum_grades.sum() + (expected_games-games_played) * replacement_score) / expected_games).round(2)


def predict_score(stats, year=2020):
    if year-1 not in stats.columns:
        return np.NaN
    if year-2 not in stats.columns:
        return stats.loc['Score', year-1]
    pred_last2 = (2*stats.loc['Score', year-1] + stats.loc['Score', year-2])/3
    return pred_last2


def get_player_id_from_name(name):
    ids = [int(x) for x in df[df['Nome']==name.upper()]['Fantacalcio_id'].unique()]
    if len(ids) == 1:
        return ids[0]
    elif len(ids) == 0:
        raise ValueError(f"Couldn't find any grades for player {name}")
        # search_id_from_name(name)
    elif len(ids) > 1:
        raise ValueError(f"Found more than 1 ID for player {name}: {ids}")
    else:
        raise ValueError("Unclear error")


def get_season_week_str(row):
    season = row['Season']
    week = row['Week']
    return f"{str(int(season))}-{str(int(season)-1999)} week {week:02d}"


def get_first_last_team(team):
    team = team.sort_values(by=['Season', 'Week'])
    team_name = team.iloc[0]['Team']
    first = get_season_week_str(team.iloc[0])
    for row in team.index:
        if team.loc[row]['Team'] == team_name:
            last = get_season_week_str(team.iloc[0])
            team = team.drop(index=row, axis=1)
        else:
            return f"{team_name} from {first} to {last}", team
    return f"{team_name} from {first} to {last}", None


def get_teams_from_fcid(fc_id):
    team = df.loc[df['Fantacalcio_id']==fc_id, ['Team', 'Week', 'Season']]
#     team.groupby(['Season', 'Team'])['Week'].agg(['min', 'max'])
    teams = list()
    while team is not None:
        first_last, team = get_first_last_team(team)
        teams.append(first_last)
    return teams


def get_roles_from_fcid(fc_id):
    role = df.loc[df['Fantacalcio_id']==fc_id, ['Ruolo', 'Week', 'Season']]
    return role.groupby('Season').first()['Ruolo']


def get_raw_stats_from_fcid(fc_id):
    stats = df.loc[df['Fantacalcio_id']==fc_id].copy()
    return stats


def player_stats(raw_stats):
    stats = OrderedDict([])
    stats['Game'] = len(raw_stats.index)
    stats['Score'] = compute_score(raw_stats)
    for col in raw_stats.columns:
        if any([col.startswith('Voto_'), col.startswith('Bonus')]):
            stats[col] = raw_stats[col].mean()
    stats['Bonus'] = raw_stats['Bonus'].mean()
    stats['Bonus_nop'] = raw_stats['Bonus_nop'].mean()
    if any(raw_stats['Ruolo']=='P'):
        stats['Goal_Conceded'] = raw_stats['Gs'].sum()
        stats['Penalty_Saved'] = raw_stats['Rp'].sum()
    elif all(raw_stats['Ruolo']!='P'):
        stats['Goal_Scored'] = raw_stats['Gf'].sum()
        stats['Penalty_Scored'] = raw_stats['Rf'].sum()
        stats['Penalty_Missed'] = raw_stats['Rs'].sum()
        stats['Assist'] = raw_stats['Ass'].sum() + raw_stats['Asf'].sum()
    else:
        raise ValueError("Role is unclear: 'P' for some but not all games")
    stats['Own_Goal'] = raw_stats['Au'].sum()
    stats['Red_Card'] = raw_stats['Esp'].sum()
    stats['Yellow_Card'] = raw_stats['Amm'].sum()
    return stats


def analyse_stats(raw_stats):
    # Total
    stats = player_stats(raw_stats)
    all_stats = pd.Series(stats).to_frame('Total')
    all_stats['Avg'] = all_stats['Total'].iloc[7:] / stats['Game']
    # Season
    seasons = raw_stats['Season'].unique()[::-1]
    stats_py = OrderedDict([(season, player_stats(raw_stats.loc[df['Season']==season])) for season in seasons])
    all_stats = all_stats.join(pd.DataFrame(stats_py), how='right')
    # Role
    ruolo = raw_stats.groupby('Season').first()[['Ruolo']].T
    # Concat
    all_stats = pd.concat([all_stats.round(2), ruolo])
    all_stats = all_stats[['Total'] + [s for s in seasons] + ['Avg']]
    return all_stats


def get_stats_from_id(name):
    try:
        fc_id = get_player_id_from_name(name)
    except ValueError:
        print(f'Found no ID for player {name}')
        return None
    raw_stats = get_raw_stats_from_fcid(fc_id)
    stats_player = analyse_stats(raw_stats)
    stats_player.columns.name = 'Period'
    stats_player.index.name = 'Stat'
    stats_player_mod = stats_player.unstack().to_frame(name).T
#     stats_player_mod = stats_player.stack().to_frame('Value').reset_index()
#     stats_player_mod['Player'] = fc_id
    return stats_player_mod



# Global Variables
df = pd.read_csv('Output_FC/output_fc.csv')
GAMES_PS = df[['Week', 'Season']].drop_duplicates().groupby('Season').count()
# Add bonuses
df['Bonus'] = df.apply(get_bonus, axis=1)
df['Bonus_nop'] = df.apply(get_bonus_nop, axis=1)
# Stats per role
avg_grade_role = df.set_index('Ruolo')[[VOTO_TYPE,'Bonus_nop']].sum(1).reset_index().groupby('Ruolo').mean()[0].round(2)
std_grade_role = df.set_index('Ruolo')[[VOTO_TYPE,'Bonus_nop']].sum(1).reset_index().groupby('Ruolo').std()[0].round(2)
# avg_grade_role = df.groupby(['Ruolo'])[['Voto_Italia','Bonus_nop']].mean().sum(1).round(2)
avg_grade_role_season = df.groupby(['Ruolo', 'Season'])[['Voto_Italia','Bonus_nop']].mean().sum(1).unstack().round(2)
REPLACEMENT_PER_ROLE = (avg_grade_role - 0.5 * std_grade_role).round(2)
# Quotes
quotes = pd.read_csv("Input_FC/Quotazioni_Fantacalcio_2020_03.csv").rename(columns={'Id': 'Fantacalcio_id'}).set_index('Nome')
big_df = pd.concat([get_stats_from_id(name) for name in quotes.index if get_stats_from_id(name) is not None])
big_df.columns = [f'{col[0]}_{col[1]}' for col in big_df.columns.values]
quotes_stats = quotes.join(big_df, how='left')
quotes_stats.fillna("-").to_csv("Output_FC/Quotes_stats.csv")
