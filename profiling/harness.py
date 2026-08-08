"""

Before profiling or measuring latency in the system, we need to start from a clean state. 

We can do this in the following steps:

1. Create a temporary clean database path
2. Create a tagged game object
3. Runs game



"""
import sqlite3
import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules"))
import engine
from strategies import thompson_sampling, explore_exploit, constant_pump
from engine import Game


PROFILING_GAME_ID = 999

seed = 10002

# Returns path of a temporary database
def fresh_db(tag: str = "default") -> str:
    
    path = os.path.join(tempfile.gettempdir(), f"latency_profiling_{tag}.db")

    engine.DATABASE_PATH = path
    
    if os.path.exists(path):
        os.remove(path)

    return path


# Returns a Game object with our 3 strategies connected to the profiling game id
def game_builder(num_balloons: int) -> Game:

    strategies = [
        thompson_sampling(), 
        explore_exploit(0.25, num_balloons),
        constant_pump(4)
    ]
    games = []
    for strat in strategies:
        game = Game([strat], seed, PROFILING_GAME_ID, num_balloons)
        game.main()
        strat.PnL = 0
        games.append(game)
    return games

# Main function
# This is the one we measure the time of
def run_game(tag: str, num_balloons: int) -> None:
    path = fresh_db(tag)
    games = game_builder(num_balloons)
    for game in games:
        game.main()
    return path

