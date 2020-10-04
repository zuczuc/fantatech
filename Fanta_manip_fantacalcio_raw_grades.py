# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 19:12:06 2020

@author: zuk-8
"""


import os
import pandas as pd
from xlrd import open_workbook



def  cd():
    return os.getcwd().replace("\\","/")


def values_from_row(sheet, row):
    return [v.value for v in sheet.row(row)]


def values_from_team(sheet, rows, cods, team):
    rs = rows[team]
    df = pd.DataFrame(
            [values_from_row(sheet, row) for row in range(*rs)],
            columns=values_from_row(sheet, cods[0]),
        ).set_index('Cod.')
    df['sv'] = df['Voto'].apply(lambda x: x in ['6*', '-'])
    df['Voto'] = df['Voto'].mask(df['Voto']=='6*', '6').\
                            mask(df['Voto']=='-', '6').\
                            astype(float)
    df['Team'] = team
    return df


def values_from_sheet(book, sheet_name):
    sheet = book.sheet_by_name(sheet_name)
    cods = [i for i,n in enumerate(sheet.col(0)) if n.value=='Cod.']
    len_sheet = len(sheet.col(0))
    separators = cods + [len_sheet]
    teams = [n.value for i,n in enumerate(sheet.col(0)) if i+1 in cods]
    rows = {t: [separators[i]+1,separators[i+1]-2] for i,t in enumerate(teams)}
    df = pd.concat([values_from_team(sheet, rows, cods, team) for team in teams])
    df = df.rename(columns={'Voto': f"Voto_{sheet_name}", 'sv': f"sv_{sheet_name}"})
    return df


def values_from_book(book):
    sheets = book.sheet_names()
    old_df = None
    for sheet_name in sheets:
        df = values_from_sheet(book, sheet_name)
        if old_df is not None:
            cols = [c for c in set(df.columns).intersection(set(old_df.columns))
                    if c not in ['Team', 'Nome', 'Ruolo']]
            check = old_df[cols].subtract(df[cols])
            if check.mean().mean() != 0 or check.std().std() != 0:
                print(f"Consistency check failed while evaluating {sheet_name}")
            old_df = old_df.join(df[[f"Voto_{sheet_name}", f"sv_{sheet_name}"]])
        else:
            old_df = df.copy()
    # cols_voto = [col for col in old_df.columns if col.startswith('Voto_')]
    # old_df['sv'] = old_df[cols_voto].apply(lambda l: any([type(x) == str for x in l]), axis=1)
    # old_df[cols_voto].mask(type(old_df[cols_voto])==str, 6)
    return old_df

def values_from_week(season, week):
    file_path = f'{cd()}/Input_FC/{season}_{season-1999}'
    file_name = f'{file_path }/Voti_Fantacalcio_Stagione_{season}-{season-1999}_Giornata_{week}.xlsx'
    book = open_workbook(file_name, on_demand=True)
    df = values_from_book(book)
    df['Week'] = week
    return df


def values_from_season(season):
    file_path = f'{cd()}/Input_FC/{season}_{season-1999}'
    xls_file_names = os.listdir(file_path)
    weeks = [w for w in range(1,39) if f'Voti_Fantacalcio_Stagione_{season}-{season-1999}_Giornata_{w}.xlsx' in xls_file_names]
    print(f'Fetching data for season {season}')
    df = pd.concat([values_from_week(season, week) for week in weeks])
    df['Season'] = season
    return df
    


def get_all_data():
    seasons = range(2015,2021)
    df = pd.concat([values_from_season(season) for season in seasons])
    # Next line never run
    df = df[['Cod.', 'Nome', 'Ruolo', 'Team', 'Week', 'Season',
         'Voto_Fantacalcio', 'sv_Fantacalcio', 'Voto_Italia', 'sv_Italia', 'Voto_Statistico', 'sv_Statistico',
         'Gf', 'Gs', 'Rp', 'Rs', 'Rf', 'Au', 'Amm', 'Esp', 'Ass', 'Asf', 'Gdv', 'Gdp'
       ]].rename(columns={'Cod.': 'Fantacalcio_id'})
    df.to_csv(f'{cd()}/Output_FC/output_fc.csv')
    return df


def players_csv(df):
    cod_name = df.reset_index()[['Fantacalcio_id','Nome']].\
                    drop_duplicates()
    cod_name['Fantacalcio_id'] = cod_name['Fantacalcio_id'].astype(int)
    # cod_name = cod_name.rename(columns={'Cod.': 'Fantacalcio_id'})
    cod_name.to_csv('DB/fantacalcio_players.csv', index=False)

df = get_all_data()
# players_csv(df)
