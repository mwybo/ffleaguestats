import ffleaguestats as ff

adl = ff.FantasyLeague(57456, 2018, current_week=10, download=False)
adl.plot_manager_rankings()