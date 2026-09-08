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
import numpy as np
from core import Context
PROFILING_GAME_ID = 999

seed = 10002


color_map = {"red": 0.2, 
                      "blue": 0.5, 
                      "purple": 0.7, 
                      "brown": 0.9}

# Returns path of a temporary database
def fresh_db(tag: str = "default") -> str:
    
    path = os.path.join(tempfile.gettempdir(), f"latency_profiling_{tag}.db")

    engine.DATABASE_PATH = path
    
    if os.path.exists(path):
        os.remove(path)

    return path


# Returns a Game object with our 3 strategies connected to the profiling game id
def game_builder(num_balloons: int) -> Game:

    
    # rng doesn't really matter for profiling

    rng = np.random.default_rng(seed)
    ctx = Context(num_balloons, list(color_map.keys()))

    strategies = [
        thompson_sampling(ctx=ctx, rng=rng), 
        explore_exploit(0.25, ctx, rng),
        constant_pump(4, ctx, rng)
    ]
    games = []
    for strat in strategies:
        game = Game([strat], seed, PROFILING_GAME_ID, num_balloons)
        strat.PnL = 0
        games.append(game)
    return games

# Main function
# This is the one we measure the time of
def run_game(tag: str, num_balloons: int) -> None:
    path = fresh_db(tag)
    games = game_builder(num_balloons)
    for game in games:
        game.main(path, color_map)
    return path

