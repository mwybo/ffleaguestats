"""
I think the goal here is to have connections that can be plugged into a league to do the same calcs no matter what the platform
"""

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import time


class BaseConnection:
    def __init__(self, league_id, season_id):
        self.league_id = league_id
        self.season_id = season_id


class FantasyProsDraftRankings:
    def __init__(self, scoring):
        if scoring not in ['standard', 'ppr', 'half-ppr']:
            raise Exception('Must selecte standard, ppr, half-ppr for arg scoring')
        self.scoring = scoring
        if scoring == 'half-ppr':
            self.url = 'https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php'

    def retrieve_df(self):
        print('Retrieving %s projections from FantasyPros' % self.scoring)
        df_season = pd.read_html(self.url)[0]
        # Remove headers
        df_season = df_season.loc[~df_season['Rank'].str.contains('Tier'), :]
        return df_season


class SleeperConnection(BaseConnection):
    def __init__(self, league_id, season_id):
        BaseConnection.__init__(self, league_id, season_id)
        self.league_info = dict()
        self.matchups = dict()

    def download(self):
        self._download_league_info()
        self._download_rosters()
        self._download_mathcups()
        self._download_player_db()
        self._download_player_stats()

    def _download_league_info(self):
        print('Downloading League Info...')
        info = requests.get('https://api.sleeper.app/v1/league/%s' % self.league_id)
        self.league_info = json.loads(info.content.decode('utf-8'))
        try:
            self.league_info['group_id']
        except KeyError:
            raise Exception('Failed to download league info')
        else:
            print('Done!')

    def _download_mathcups(self):
        print('Downloading matchups...')
        self.matchups = {}
        for week in range(1, 17):
            print(week, end='.. ')
            if week == 16:
                print('')
            matchups = requests.get('https://api.sleeper.app/v1/league/%s/matchups/%s' % (self.league_id, week))
            self.matchups[str(week)] = json.loads(matchups.content.decode('utf-8'))

    def _download_rosters(self):
        print('Downloading Rosters...')
        rosters = requests.get('https://api.sleeper.app/v1/league/%s/rosters' % (self.league_id))
        self.rosters = json.loads(rosters.content.decode('utf-8'))

    def _download_player_db(self):
        fname = 'player_db.json'

        def download_and_save():
            players = requests.get('https://api.sleeper.app/v1/players/nfl')
            json.dump(json.loads(players.content.decode('utf-8')), open(fname, 'w'))

        if os.path.exists(fname):
            if os.path.getmtime(fname) > (time.time() - 60*60*24):
                pass
            else:
                print('Player DB is out of date... downloading')
                download_and_save()
                print('Done!')
        else:
            print('Player DB has not yet been downloaded... downloading')
            download_and_save()
            print('Done!')
        self.player_db = json.load(open(fname, 'r'))

    def _download_player_stats(self):
        print('Downloading Player Stats...')
        self.player_stats = dict()
        season_stats = requests.get('https://api.sleeper.app/v1/stats/nfl/regular/%s' % self.season_id)
        self.player_stats.update(season=json.loads(season_stats.content.decode('utf-8')))
        for week in range(1, 17):
            print(week, end='.. ')
            if week == 16:
                print('')
            week_stats = requests.get('https://api.sleeper.app/v1/stats/nfl/regular/%s/%s' % (self.season_id, week))
            tmp = {str(week): json.loads(week_stats.content.decode('utf-8'))}
            self.player_stats.update(tmp)




class ESPNConnection:
    def __init__(self, league_id, season_id, **kwargs):
        self.league_id = league_id
        self.season_id = season_id
        self.scoreboards = {}
        self.boxscores = {}

    def download(self):
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

    def load(self):
        self.scoreboards = json.load(open('%s_%s_sbs.json' % (self.league_id, self.season_id), 'rb'))
        self.boxscores = json.load(open('%s_%s_bss.json' % (self.league_id, self.season_id), 'rb'))


if __name__ == '__main__':
    # conn = SleeperConnection(league_id=402964075534880768, season_id=2018)
    # conn.download()

    fp = FantasyProsDraftRankings('half-ppr')
    df = fp.retrieve_df()
