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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Classes
import simple_strategies
from simple_strategies import explore_then_exploit, constant_pump, thompson_sampling
from Classes import Game

PROFILING_GAME_ID = 999


# Returns path of a temporary database
def fresh_db(tag: str = "default") -> str:
    
    path = os.path.join(tempfile.gettempdir(), f"latency_profiling_{tag}.db")

    Classes.DATABASE_PATH = path
    simple_strategies.DATABASE_PATH = path

    if os.path.exists(path):
        os.remove(path)

    return path


# Returns a Game object with our 3 strategies connected to the profiling game id
def game_builder(num_balloons: int) -> Game:

    players = [
        thompson_sampling(PROFILING_GAME_ID), 
        explore_then_exploit(0.25, num_balloons, PROFILING_GAME_ID, 1),
        constant_pump(4)
    ]

    return Game(players, num_balloons, PROFILING_GAME_ID)

# Main function
# This is the one we measure the time of
def run_game(tag: str, num_balloons: int) -> None:
    path = fresh_db(tag)
    game = game_builder(num_balloons)
    game.start()
    return path

# Counts how many turns in a game
def count_turns(db_path:str) -> int:
    conn = sqlite3.Connection(db_path)
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT COUNT(*) FROM game_{PROFILING_GAME_ID}")
        count = cur.fetchone()[0]
        return count
    finally:
        conn.close()