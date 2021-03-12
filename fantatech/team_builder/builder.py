from .. import formations
from ..visualization import stats
from ..constants import CURRENT_YEAR
from ..analysis.aggregators import aggregate_stats, aggregate_players_stats
from ..formations import Ruolo, get_missing_roles
from ..data_loaders.players import load_players_list

from IPython.display import display, HTML
import pandas as pd
import numpy as np
from matplotlib.colors import ListedColormap, rgb2hex
import seaborn as sns


class Team(object):

    def __init__(self, df, player_ids_and_costs, budget=400, target_formations=None):
        self.df = df
        self.df_players = load_players_list()
        self.player_id_2_cost = dict(player_ids_and_costs)
        self.player_ids = list(self.player_id_2_cost.keys())
        self.costs = list(self.player_id_2_cost.values())
        self.budget = budget
        self.target_formations = target_formations
        self.df['Cost'] = df['Id'].map(self.player_id_2_cost)

    def display(self):
        display(HTML('<font size="+1"><b>Team Builder</b></font>'))

        # Players summaries
        cols = ['Id', 'Nome', 'Squadra', 'RuoloMantra', 'QuotazioneAttuale']
        self.df_players['Nome'] = self.df_players['Nome'].str.title()
        summaries = self.df_players.loc[self.df_players['Id'].isin(self.player_ids), cols].rename(columns={
            'Team' : 'Squadra',
            'RuoloMantra' : 'Mantra',
            'QuotazioneAttuale' : 'Quotazione',
        }).set_index('Nome')
        summaries['Reparto'] =  summaries['Mantra'].apply(mantra_2_ruolo)
        summaries['Costo'] = summaries['Id'].map(self.player_id_2_cost)
        summaries['Costo%'] = summaries['Costo'] / self.budget


        # summaries = aggregate_stats(self.df.loc[self.df['Id'].isin(self.player_ids) & self.df['Season'].isin({CURRENT_YEAR})], by=['Id', 'Ruolo'])[['Cost']].rename(columns={'Cost' : 'Costo'}).reset_index('Ruolo')

        stats = aggregate_players_stats(self.df, self.player_ids, years=CURRENT_YEAR - 1, multiplayer=True)
        summaries = summaries.join(stats[['Fv*', 'FvExtra', 'GP%']], how='left')
        summaries = summaries.drop('Id', axis=1)

        # Sort by Mantra role
        summaries['_Mantra'] = pd.Categorical(summaries['Mantra'].str.split(';', expand=True)[0].str.upper(), [x.name for x in Ruolo])
        summaries = summaries.sort_values('_Mantra').drop('_Mantra', axis=1)


        # Recap
        recap = pd.DataFrame({
            'Budget' : self.budget,
            'Spent' : sum(self.costs),
            'Left': self.budget - sum(self.costs),
            'Number of players': len(self.player_ids),
            'TotFvExtra': np.round(summaries['FvExtra'].sum() * 11 / len(self.player_ids), decimals=2),
        }, index=['Recap'])
        display(recap)

        # Cost per role
        costs_per_role = summaries.groupby('Reparto')[['Costo']].agg(['count', 'sum'])
        costs_per_role = costs_per_role.loc[[x for x in ['Portieri', 'Difesa', 'Esterni', 'Centrocampo', 'Trequarti', 'Attacco'] if x in costs_per_role.index]]
        costs_per_role.columns = ['Giocatori', 'Costo']
        costs_per_role['Costo%'] = costs_per_role['Costo'] / self.budget
        display(
            costs_per_role.style
            .format({'Costo': '{:.0f}', 'Costo%': '{:.1%}'})
            .background_gradient('Reds', subset=['Costo%'])
        )

        cmap = ListedColormap(sns.diverging_palette(10, 240, n=21).as_hex())
        max_fv_extra = summaries['FvExtra'].abs().max()
        background_gradient = lambda x: f'background-color: {rgb2hex(cmap(x / (2 * max_fv_extra) + 0.5)[:3])}'

        display(
            summaries[['Squadra', 'Mantra', 'Reparto', 'GP%', 'Fv*', 'FvExtra', 'Quotazione', 'Costo', 'Costo%']].style
            .format({'Costo': '{:.0f}', 'Costo%': '{:.1%}', 'Fv*': '{:.2f}', 'GP%': '{:.1%}', 'FvExtra': '{:.2f}'})
            .background_gradient('Reds', subset=['Costo%'])
            .background_gradient('Greens', subset=['GP%'])
            .applymap(background_gradient, subset=['FvExtra'])
            .highlight_null('lightgray')
        )

        # Feasible formations
        display(HTML('<font size="+0"><b>Feasible formations</b></font>'))
        print(", ".join(x.name[1:] for x in formations.get_feasible_formations(self.df, self.player_ids)))

        if self.target_formations:
            for t in self.target_formations:
                display(HTML(f'<font size="+0"><b>{t.name[1:]}</b></font>'))
                out = formations.get_missing_roles(self.df, self.player_ids, t)
                out = (
                    out.style
                    .applymap(_missing_role_count_2_color, subset=[r.name for r in Ruolo if r.name in out.columns])
                )
                display(out)



def _missing_role_count_2_color(x):
    if x <= -2:
        return 'background-color: crimson'
    elif x == -1:
        return 'background-color: salmon'
    elif x == 1:
        return 'background-color: lightgreen'
    elif x >= 2:
        return 'background-color: mediumseagreen'

_mantra_2_ruolo = {
    'Por' : 'Portieri',
    'Dc'  : 'Difesa',
    'Ds'  : 'Esterni',
    'Dd'  : 'Esterni',
    'E'   : 'Esterni',
    'M'   : 'Centrocampo',
    'C'   : 'Centrocampo',
    'T'   : 'Trequarti',
    'W'   : 'Trequarti',
    'A'   : 'Attacco',
    'Pc'  : 'Attacco',
}

def mantra_2_ruolo(x):
    for y in x.split(';'):
        return _mantra_2_ruolo[y]