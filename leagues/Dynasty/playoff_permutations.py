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
    matches = [#'MW:TC', 'SL:BS', 'CM:SS', 'JL:CV', 'JK:TK', 'JZ:TG',  # WEEK 10
               # 'SS:MW', 'TC:SL', 'CV:CM', 'TK:JL', 'JZ:JK', 'BS:TG',  # WEEK 11
               'CV:MW', 'SS:SL', 'TK:CM', 'JZ:JL', 'BS:JK', 'TC:TG',  # WEEK 12
               'MW:TK', 'SL:CV', 'CM:JZ', 'JL:BS', 'JK:TC', 'TG:SS']  # WEEK 13

    matchups_remain = len(matches)  # number of total matches left
    combos = pow(2, matchups_remain)
    format_str = '0{}b'.format(matchups_remain)  # will formaat a binary string that simulates every match

    print('Simulating %s combinations' % combos)
    for i in range(0, combos):  # loop thru all of the combinations of possible matches
        if i%1000 == 0:
            print('Completed %s simulations' % i)

        binary_str = format(i, format_str)
        teams = init_teams()

        # Now go thru each digit of the binary, where each digit is a match, and simulate
        for i_match, outcome in enumerate(binary_str):
            t1, t2 = matches[i_match].split(':')
            if outcome == '0':
                teams[t1].wins += 1
                teams[t2].losses += 1
            else:
                teams[t2].wins += 1
                teams[t1].losses += 1

        # print('Simulation %s' % i)
        # for k, t in teams.items():
        #     print(t.name, t.wins, t.losses)

        # Cram the results into a df for easy sorting
        df = pd.DataFrame()
        for key, team in teams.items():
            df = df.append(team.dump_to_df())
        df = df.sort_values(by=['wins', 'points_for'], ascending=False)
        df = df.reset_index(drop=True)
        df_top6 = df.iloc[0:6]
        playoff_teams = list(df_top6['name'])
        for t in playoff_teams:
            playoff_chances[t] += 1

    # Now that I'm thru it all, lets display playoff chances
    playoff_pct = {}
    for k, t in playoff_chances.items():
        playoff_pct[k] = np.round((t / combos) * 100, 2)
    playoff_pct = pd.Series(playoff_pct)
    playoff_pct = playoff_pct.sort_values(ascending=False)



    print('Completed in', (time.time()-start))