"""
basically i think I could make a class League that had subclasses of Teams that had all kinds of fun functions to calculate
all of these stats by downloading the league stats, making all the Teams from the dictionary, and plotting calculating visualizing

Things I'd need to do outside of it
1 SImulation of possible outcomes
"""
import requests
import json
import pandas as pd


class FantasyLeague:
    def __init__(self, league_id, season_id, download=True):
        # misc init
        self.scoreboards = {}
        self.boxscores = {}

        # Init league and inputs
        self.league_id = league_id
        self.season_id = season_id
        if download:
            self.download_espn_league_results()
        print('Loading boxscores and scoreboards')
        self.load_league_results()
        print('Extracting player_df')
        self.player_df = self._build_player_df()
        print('Calculating manager rankings')
        self.manager_rankings = self.calculate_manager_rankings()

    """
    ------- DATA INITIALIZATION ------
    """
    def download_espn_league_results(self):
        leagueId, seasonId = self.league_id, self.season_id

        sbs = {}
        bss = {}

        print('Week', end=' ')
        for week in range(1, 17):
            print(week, end=' .. ')

            sb = requests.get('http://games.espn.com/ffl/api/v2/scoreboard',
                              params={'leagueId': leagueId, 'seasonId': seasonId, 'matchupPeriodId': week})
            sb = sb.json()
            sbs[week] = sb
            bss[week] = {}

            # loop through matchups that week
            for match in range(len(sb['scoreboard']['matchups'])):
                homeId = sb['scoreboard']['matchups'][match]['teams'][0]['team']['teamId']

                r = requests.get('http://games.espn.com/ffl/api/v2/boxscore',
                                 params={'leagueId': leagueId, 'seasonId': seasonId,
                                         'teamId': homeId, 'matchupPeriodId': week},
                                 # cookies={'SWID': swid, 'espn_s2': espn}
                                 )
                r = r.json()
                bss[week][match] = r

        print('\nSaving to json..')
        json.dump(sbs, open('%s_%s_sbs.json' % (leagueId, seasonId), 'w'))
        json.dump(bss, open('%s_%s_bss.json' % (leagueId, seasonId), 'w'))
        print('Complete.')

    def load_league_results(self):
        self.scoreboards = json.load(open('%s_%s_sbs.json' % (self.league_id, self.season_id), 'rb'))
        self.boxscores = json.load(open('%s_%s_bss.json' % (self.league_id, self.season_id), 'rb'))

    def build_player_df(self):
        sbs = self.scoreboards.copy()
        bss = self.boxscores.copy()

        # Pick out the basic stats per player, per week, and assign them to a team
        slots = {0: 'QB', 2: 'RB', 4: 'WR', 6: 'TE',
                 16: 'D/ST', 17: 'K', 20: 'BE', 23: 'FLEX'}

        # rows will be by player by week
        df = pd.DataFrame(columns=['playerName', 'matchupPeriodId',
                                   'slotId', 'position', 'bye', 'appliedStatTotal',
                                   'teamAbbrev', 'wonMatchup'])

        for week in range(1, 17):
            week = str(week)
            for match in range(len(sbs[week]['scoreboard']['matchups'])):
                # match = str(match)
                homeId = sbs[week]['scoreboard']['matchups'][match]['teams'][0]['team']['teamId']
                winner = sbs[week]['scoreboard']['matchups'][match]['winner']

                # loop through home (0) and away (1)
                for team in range(2):
                    # boolean for who won this matchup
                    winb = False
                    if (winner == 'away' and team == 1) or (winner == 'home' and team == 0):
                        winb = True

                    # fantasy team info (dict)
                    # team = str(team)
                    match_bss = str(match)
                    tinfo = bss[week][match_bss]['boxscore']['teams'][team]['team']

                    # all players on that team info (array of dicts)
                    ps = bss[week][match_bss]['boxscore']['teams'][team]['slots']

                    # loop through players
                    for k, p in enumerate(ps):
                        # players on bye/injured won't have this entry
                        try:
                            pts = p['currentPeriodRealStats']['appliedStatTotal']
                        except KeyError:
                            pts = 0

                        # there is some messiness in the json so just skip
                        try:
                            # get player's position. this is a bit hacky...
                            pos = p['player']['eligibleSlotCategoryIds']
                            for s in [20, 23]:
                                if pos.count(s) > 0:
                                    pos.remove(s)
                            pos = slots[pos[0]]

                            # add it all to the DataFrame
                            df = df.append({'playerName': p['player']['firstName'] + ' ' + p['player']['lastName'],
                                            'matchupPeriodId': week,
                                            'slotId': p['slotCategoryId'],
                                            'position': pos,
                                            'bye': True if p['opponentProTeamId'] == -1 else False,
                                            'appliedStatTotal': pts,
                                            'teamAbbrev': tinfo['teamAbbrev'],
                                            'wonMatchup': winb},
                                           ignore_index=True)
                        except KeyError:
                            continue
        return df

    def _build_player_df(self):
        sbs = self.scoreboards.copy()
        bss = self.boxscores.copy()

        # Pick out the basic stats per player, per week, and assign them to a team
        slots = {0: 'QB', 2: 'RB', 4: 'WR', 6: 'TE',
                 16: 'D/ST', 17: 'K', 20: 'BE', 23: 'FLEX'}

        # rows will be by player by week
        df = pd.DataFrame(columns=['playerName', 'matchupPeriodId',
                                   'slotId', 'position', 'bye', 'appliedStatTotal',
                                   'teamAbbrev', 'wonMatchup'])

        for week in range(1, 17):
            week = str(week)
            for match in range(len(sbs[week]['scoreboard']['matchups'])):
                # match = str(match)
                homeId = sbs[week]['scoreboard']['matchups'][match]['teams'][0]['team']['teamId']
                winner = sbs[week]['scoreboard']['matchups'][match]['winner']

                # loop through home (0) and away (1)
                for team in range(2):
                    # boolean for who won this matchup
                    winb = False
                    if (winner == 'away' and team == 1) or (winner == 'home' and team == 0):
                        winb = True

                    # fantasy team info (dict)
                    # team = str(team)
                    match_bss = str(match)
                    tinfo = bss[week][match_bss]['boxscore']['teams'][team]['team']

                    # all players on that team info (array of dicts)
                    ps = bss[week][match_bss]['boxscore']['teams'][team]['slots']

                    # loop through players
                    for k, p in enumerate(ps):
                        # players on bye/injured won't have this entry
                        try:
                            pts = p['currentPeriodRealStats']['appliedStatTotal']
                        except KeyError:
                            pts = 0

                        # there is some messiness in the json so just skip
                        try:
                            # get player's position. this is a bit hacky...
                            pos = p['player']['eligibleSlotCategoryIds']
                            for s in [20, 23]:
                                if pos.count(s) > 0:
                                    pos.remove(s)
                            pos = slots[pos[0]]

                            # add it all to the DataFrame
                            df = df.append({'playerName': p['player']['firstName'] + ' ' + p['player']['lastName'],
                                            'matchupPeriodId': week,
                                            'slotId': p['slotCategoryId'],
                                            'position': pos,
                                            'bye': True if p['opponentProTeamId'] == -1 else False,
                                            'appliedStatTotal': pts,
                                            'teamAbbrev': tinfo['teamAbbrev'],
                                            'wonMatchup': winb},
                                           ignore_index=True)
                        except KeyError:
                            continue
        return df

    """
    ----- CALCULATIONS ----
    """
    def calculate_manager_rankings(self, current_week=16):
        sbs = self.boxscores.copy()
        bss = self.boxscores.copy()

        df = self.player_df

        manager_rankings = pd.DataFrame(columns=['week', 'teamAbbrev', 'bestBall', 'actual', 'realization'])
        teams = df['teamAbbrev'].unique()
        roster = {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'D/ST': 1, 'FLX': 2}
        for week, all_players in df.groupby('matchupPeriodId'):
            if int(week) >= current_week:
                continue
            for team, players in all_players.groupby('teamAbbrev'):
                # 20 is bench, 21 is IR
                starters = players.loc[~(players['slotId'].isin([20, 21]))]
                starters_score = starters['appliedStatTotal'].sum() \
                    # Init the best ball score, start to loop thru the roster
                best_ball_score = 0
                for pos_id, num_start in roster.items():
                    if pos_id is not 'FLX':
                        pos = players.loc[players['position'] == pos_id]
                    else:
                        pos = players.loc[players['position'].isin(['WR', 'RB'])]
                    # Get the best in the position
                    best_in_pos = pos.sort_values(by='appliedStatTotal', ascending=False)[:num_start]
                    # Remove from the players dictionary above so they can't be used again when we get to flx
                    players = players.drop(best_in_pos.index)
                    best_ball_score += best_in_pos['appliedStatTotal'].sum()
                delta = best_ball_score - starters_score
                realization = starters_score / best_ball_score
                manager_rankings = manager_rankings.append({'week': week,
                                                            'teamAbbrev': team,
                                                            'bestBall': best_ball_score,
                                                            'actual': starters_score,
                                                            'realization': realization,
                                                            'ptDelta': delta}, ignore_index=True)
        manager_rankings['week'] = manager_rankings['week'].astype(int)
        return manager_rankings
    """
    ----- VISUALIZATIONS ----
    """
if __name__ == '__main__':
    ADL = FantasyLeague(57456, 2018, download=False)
