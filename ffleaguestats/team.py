"""
The goal is to make a Team class that team specific calculations can live inside of
"""

class Team:
    def __init__(self):
        self.rosters = {}
        self.current_roster = {}
        self.matchups = {}
