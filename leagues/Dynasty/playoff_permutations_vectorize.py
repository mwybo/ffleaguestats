from itertools import permutations
from copy import deepcopy
import pandas as pd
import numpy as np
import time

class Team:
    def __init__(self, wins=0, losses=0, name=None, ID=None, points_for=0):
        self.wins = wins
        self.losses = losses
        self.name = name
        self.num_playoffs = 0
        self.ID = ID
        self.points_for = points_for

    def dump_to_df(self):
        return pd.DataFrame(data=[[self.name, self.wins, self.losses, self.points_for]], columns=['name', 'wins', 'losses', 'points_for'])


def init_teams():
    teams = deepcopy(ADL_teams)
    return teams


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

if __name__ == '__main__':
    start = time.time()
    ADL_teams = dict(JK=Team(8, 3, 'Threat Level Midnight', 'JK', 1466.6),
                     TG=Team(9, 2, 'The Flu Draft', 'TG', 1471.9),
                     BS=Team(7, 4, 'Britton\'s Team', 'BS', 1451.3),
                     CV=Team(5, 6, 'Team Vinson', 'CV', 1288.1),
                     SL=Team(6, 5, 'Team Loreaux', 'SL', 1331.4),
                     TK=Team(5, 6, 'Team Kuck', 'TK', 1220.4),
                     CM=Team(5, 6, 'Matre\'s Team', 'CM', 1040),
                     JL=Team(5, 6, 'Education Nation', 'JL', 1189.6),
                     JZ=Team(4, 7, 'Zippy Something', 'JZ', 1350.6),
                     MW=Team(5, 6, 'Atleast I Have FanDuel', 'MW', 1390.4),
                     SS=Team(4, 7, 'Team Rockstar', 'SS', 1257.2),
                     TC=Team(3, 8, 'Cincinnati Indians', 'TC', 1191.6)
                     )

    playoff_chances = {}
    for key, team in ADL_teams.items():
        playoff_chances[team.name] = 0

    # Going to manually simulate for now
    weeks_remain = 2
    matches = [#'MW:TC', 'SL:BS', 'CM:SS', 'JL:CV', 'JK:TK', 'JZ:TG',  # WEEK 10
               'SS:MW', 'TC:SL', 'CV:CM', 'TK:JL', 'JZ:JK', 'BS:TG',  # WEEK 11
               'CV:MW', 'SS:SL', 'TK:CM', 'JZ:JL', 'BS:JK', 'TC:TG',  # WEEK 12
               'MW:TK', 'SL:CV', 'CM:JZ', 'JL:BS', 'JK:TC', 'TG:SS']  # WEEK 13

    matchups_remain = len(matches)  # number of total matches left
    combos = pow(2, matchups_remain)
    format_str = '0{}b'.format(matchups_remain)  # will formaat a binary string that simulates every match

    print('Simulating %s combinations' % combos)
    # Generate all of the outcomes to the matches
    binary_list = []
    for i in range(0, combos):  # loop thru all of the combinations of possible matches
        if i%1000 == 0:
            print('Completed %s simulations' % i)

        binary_str = format(i, format_str)
        binary_list.append([int(x) for x in binary_str])

    df_outcomes = pd.DataFrame(data=binary_list, columns=matches)
    del binary_list

    # Now lets turn that in to wins and losses
    df_w = pd.DataFrame(data=np.zeros((len(df_outcomes), len(ADL_teams.keys()))), columns=ADL_teams.keys())

    for match_str in df_outcomes.columns:
        match = df_outcomes[match_str]
        t1 = match_str.split(':')[0]
        t2 = match_str.split(':')[1]

        df_w.loc[match == 0, t1] += 1
        df_w.loc[match == 1, t2] += 1

    # Come up with the final records.. in an even league I only need wins
    for t in df_w.columns:
        df_w[t] = df_w[t] + ADL_teams[t].wins

    df_points = pd.DataFrame(data=[[x.points_for for x in ADL_teams.values()]], columns=ADL_teams.keys())
    df_points = df_points.transpose()
    df_points.columns = ['points']
    del df_outcomes

    def rank_playoff(x):
        """
        x is a pandas DataFrame Row
        """
        tmp = pd.DataFrame(data=x)
        tmp.columns = ['wins']
        tmp = tmp.join(df_points).sort_values(by=['wins', 'points'], ascending=False)
        tmp['playoff'] = 0
        tmp.loc[tmp.iloc[0:6].index.values, 'playoff'] = 1
        return tmp['playoff']

    from tqdm import tqdm
    tqdm.pandas()

    start = time.time()
    df_playoff = df_w.progress_apply(rank_playoff, axis=1)
    print('Completed in', (time.time()-start))
    df_playoff_pct = 100 * (df_playoff.sum() / len(df_playoff))
    df_playoff_pct = df_playoff_pct.sort_values(ascending=False)
    print(df_playoff_pct)
