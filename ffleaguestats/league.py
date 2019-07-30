from connections import SleeperConnection
from connections import FantasyProsDraftRankings
from team import Team
import numpy as np

class League:
    def __init__(self, league_id, season_id, week=16, platform='Sleeper'):
        self.platform = platform
        self.season_id = season_id
        self.league_id = league_id
        self.rosters = dict()
        self.matchups = dict()
        self.player_db = dict()
        self.player_stats = dict()
        self.league_info = dict()
        self.retrieve_data()

    def retrieve_data(self):
        if self.platform == 'Sleeper':
            conn = SleeperConnection(league_id=self.league_id, season_id=self.season_id)
            conn.download()

            # map the data back out
            self.league_info = conn.league_info
            self.rosters = conn.rosters
            self.matchups = conn.matchups
            self.player_db = conn.player_db
            self.player_stats = conn.player_stats


    def _calculate_roster_strength(self):
        proj_df = FantasyProsDraftRankings('half-ppr').retrieve_df()
        # Make some useful columns
        # proj_df['Name+Team'] = proj_df['Name'] +
        proj_df['Position'] = proj_df['Pos'].str[:2]
        proj_df['In Position Rank'] = proj_df['Pos'].str[2::]
        proj_df = proj_df.dropna(['In Position Rank'], axis='columns')

        # Split into positions
        projections = {}
        # for



if __name__ == '__main__':
    adl = League(league_id=402964075534880768, season_id=2019)
    adl._calculate_roster_strength()