import enum
import itertools
import pandas as pd


class Ruolo(enum.Enum):
    POR = 'POR'
    DC  = 'DC'
    DD  = 'DD'
    DS  = 'DS'
    M   = 'M'
    C   = 'C'
    E   = 'E'
    W   = 'W'
    T   = 'T'
    A   = 'A'
    PC  = 'PC'

    def __gt__(self, other):
        # To support sort
        return self.value > other.value


class Formation(enum.Enum):

    _343 = [
        Ruolo.POR,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.E,
        [Ruolo.C, Ruolo.M],
        Ruolo.C,
        Ruolo.E,
        [Ruolo.W, Ruolo.A],
        [Ruolo.A, Ruolo.PC],
        [Ruolo.W, Ruolo.A],
    ]

    _3412 = [
        Ruolo.POR,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.E,
        [Ruolo.C, Ruolo.M],
        Ruolo.C,
        Ruolo.E,
        Ruolo.T,
        [Ruolo.A, Ruolo.PC],
        [Ruolo.A, Ruolo.PC],
    ]

    _3421 = [
        Ruolo.POR,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DC,
        [Ruolo.E, Ruolo.W],
        Ruolo.M,
        [Ruolo.C, Ruolo.M],
        Ruolo.E,
        Ruolo.T,
        [Ruolo.A, Ruolo.PC],
        [Ruolo.A, Ruolo.T],
    ]

    _352 = [
        Ruolo.POR,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DC,
        [Ruolo.E, Ruolo.W],
        [Ruolo.C, Ruolo.M],
        Ruolo.M,
        Ruolo.C,
        Ruolo.E,
        [Ruolo.A, Ruolo.PC],
        [Ruolo.A, Ruolo.PC],
    ]

    _3511 = [
        Ruolo.POR,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DC,
        [Ruolo.E, Ruolo.W],
        Ruolo.M,
        Ruolo.C,
        Ruolo.M,
        [Ruolo.E, Ruolo.W],
        [Ruolo.A, Ruolo.T],
        [Ruolo.A, Ruolo.PC],
    ]

    _433 = [
        Ruolo.POR,
        Ruolo.DD,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DS,
        [Ruolo.M, Ruolo.C],
        Ruolo.M,
        Ruolo.C,
        [Ruolo.W, Ruolo.A],
        [Ruolo.A, Ruolo.PC],
        [Ruolo.W, Ruolo.A],
    ]

    _4312 = [
        Ruolo.POR,
        Ruolo.DD,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DS,
        [Ruolo.M, Ruolo.C],
        Ruolo.M,
        Ruolo.C,
        Ruolo.T,
        [Ruolo.A, Ruolo.PC],
        [Ruolo.A, Ruolo.PC],
    ]

    _442 = [
        Ruolo.POR,
        Ruolo.DD,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DS,
        [Ruolo.E, Ruolo.W],
        [Ruolo.M, Ruolo.C],
        Ruolo.C,
        Ruolo.E,
        [Ruolo.A, Ruolo.PC],
        [Ruolo.A, Ruolo.PC],
    ]

    _4141 = [
        Ruolo.POR,
        Ruolo.DD,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DS,
        [Ruolo.E, Ruolo.W],
        [Ruolo.C, Ruolo.T],
        Ruolo.M,
        Ruolo.T,
        Ruolo.W,
        [Ruolo.A, Ruolo.PC],
    ]

    _4411 = [
        Ruolo.POR,
        Ruolo.DD,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DS,
        [Ruolo.E, Ruolo.W],
        Ruolo.M,
        Ruolo.C,
        [Ruolo.E, Ruolo.W],
        [Ruolo.A, Ruolo.T],
        [Ruolo.A, Ruolo.PC],
    ]

    _4231 = [
        Ruolo.POR,
        Ruolo.DD,
        Ruolo.DC,
        Ruolo.DC,
        Ruolo.DS,
        Ruolo.M,
        [Ruolo.M, Ruolo.C],
        [Ruolo.T, Ruolo.W],
        Ruolo.T,
        Ruolo.A,
        [Ruolo.A, Ruolo.PC],
    ]



def players_2_roles(df, player_ids):
    from .analysis.stats import get_players_summaries

    summaries = get_players_summaries(df, player_ids)
    return {
        player_id: [enum_lookup(Ruolo, x) for x in row.Mantra.split(';')]
        for player_id, row in zip(player_ids, summaries.itertuples())
    }

def get_roles_counts(roles):
    out = []
    for roles_ in unpack_roles(roles):
        counts = {}
        for role in roles_:
            if role not in counts:
                counts[role] = 1
            else:
                counts[role] += 1
        out.append(counts)
    return out

def formation_2_roles_counts(formation):
    return get_roles_counts(formation.value)


def players_2_roles_counts(df, player_ids):
    roles = players_2_roles(df, player_ids).values()
    return get_roles_counts(roles)


def formation_is_feasible(df, player_ids, formation):
    formation_roles_counts = formation_2_roles_counts(formation)
    players_roles_counts = players_2_roles_counts(df, player_ids)
    for formation_roles_counts_, players_roles_counts_ in itertools.product(formation_roles_counts, players_roles_counts):
        if formation_roles_counts_.keys() == players_roles_counts_.keys() and all(players_roles_counts_[k] >= formation_roles_counts_[k] for k in players_roles_counts_.keys()):
            return True
    return False


def get_feasible_formations(df, player_ids):
    players_roles_counts = players_2_roles_counts(df, player_ids)
    out = []
    for formation in Formation:
        formation_roles_counts = formation_2_roles_counts(formation)
        for formation_roles_counts_, players_roles_counts_ in itertools.product(formation_roles_counts, players_roles_counts):
            if all(k in players_roles_counts_ and players_roles_counts_[k] >= formation_roles_counts_[k] for k in formation_roles_counts_.keys()):
                out.append(formation)
                break
    return out


def get_missing_roles(df, player_ids, formation):
    players_roles_counts = players_2_roles_counts(df, player_ids)
    formation_roles_counts = formation_2_roles_counts(formation)
    out = []
    for formation_roles_counts_, players_roles_counts_ in itertools.product(formation_roles_counts, players_roles_counts):
        diffs = pd.Series(players_roles_counts_).subtract(pd.Series(formation_roles_counts_), fill_value=0)
        out.append(diffs)
    out = pd.DataFrame(out).fillna(0).astype(int).drop_duplicates()
    out.columns = [x.value for x in out.columns]
    out = out[[r.value for r in Ruolo if r.value in out.columns]]

    # Enrichment
    players_missing = out.where(out < 0).sum(axis=1).astype(int)
    roles_missing = out.apply(lambda x: ','.join(out.columns[x < 0]), axis=1)
    depth = out.min(axis=1)
    roles_min_depth = out.apply(lambda x: ','.join(out.columns[x == x.min()]), axis=1)
    out['playersMissing'] = players_missing
    out['depth'] = depth
    out['rolesMissing'] = roles_missing
    out['rolesMinDepth'] = roles_min_depth
    out = out.drop_duplicates(subset=['playersMissing', 'rolesMissing'])
    return out.sort_values(['playersMissing', 'depth'], ascending=False).reset_index(drop=True).iloc[:5]


def enum_lookup(cls, value):
    if isinstance(value, str):
        return cls(value.upper())
    return value


def unpack_roles(roles):
    roles = [([x] if isinstance(x, Ruolo) else x) for x in roles]
    return list(itertools.product(*roles))
