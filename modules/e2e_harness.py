
import json
import yaml
from itertools import combinations
from pathlib import Path
import numpy as np
from engine import Game
from strategies import Strategy
from core import Context
import sqlite3
from sql_handling import SQL_handling
import os 
import sys
import time
import pandas as pd

"""
yaml dict format:
{'master_seed': 10111, 
'num_seeds': 50, 
'num_balloons': 100, 
'multiplayer_mode': 0, 
'strategies': [{'name': 'constant_pump', 'params': {'pump_times': 5}}, 
                {'name': 'thompson_sampling', 'params': None}], 
'color_map': {'red': 0.2, 'blue': 0.4, 'orange': 0.7}}
"""

# Checks if the user's yaml document contains valid data
# passes on the yaml dictionary used in build_games() if everything is valid
def parse_inputs(yaml_path: str) -> dict:

    with open(yaml_path) as f:
        raw_yaml = yaml.safe_load(f)

    # 1. Check if strategy names are in register
    valid_strategies = check_strat_names(raw_yaml)

    # 2. Check if parameters are correct type
    valid_parameters = check_params(raw_yaml)

    # 3. Check game settings
    valid_game_settings = check_game_settings(raw_yaml)

    if all([valid_game_settings, valid_parameters, valid_strategies]):
        return raw_yaml

# Builds the correct games from a GameConfigs object
def build_games(raw_yaml: dict) -> list[Game]:
    Game_objects = []

    # Sort strategies 
    raw_yaml["strategies"].sort(key=lambda x: x["name"])

    # Generate balloon seeds
    master_seed = raw_yaml["master_seed"]
    num_seeds = raw_yaml["num_seeds"]
    num_strategies = len(raw_yaml["strategies"])
    rng = np.random.default_rng(master_seed)
    if num_seeds == 1:
        balloon_seeds = [master_seed]

    else:
        balloon_seeds = list(rng.integers(low=10, high=10000, size=num_seeds))

    ctx = Context(raw_yaml["num_balloons"], list(raw_yaml["color_map"].keys()))


    # Multiplayer = ?
    if raw_yaml["multiplayer"] == 1:
        # Multiplayer mode
        # Generate kC2x2n seeds
      

        for i in range(num_seeds):
            # Every matchup round robin
            rng2 = np.random.default_rng(balloon_seeds[i])
            strategy_seeds = list(rng2.integers(low=10, high=10000, size=num_strategies*(num_strategies-1)*num_seeds))
            for a, b in combinations(raw_yaml["strategies"], 2):
                strategies = strat_instance([a, b], strategy_seeds, ctx)
                balloon_seed = balloon_seeds[i]
                game_id = str(balloon_seed) + "_" + strategies[0].name + "_" + strategies[1].name
                num_balloons = ctx.num_balloons
                game = Game(strategies, balloon_seed, game_id, num_balloons)
                Game_objects.append(game)


    else:
        # Singleplayer mode
        
        for i in range(num_seeds):
            rng2 = np.random.default_rng(balloon_seeds[i])
            strategy_seeds = list(rng2.integers(low=10, high=10000, size=num_strategies))
            strategies = strat_instance(raw_yaml["strategies"], strategy_seeds, ctx)
            balloon_seed = balloon_seeds[i]
            num_balloons = ctx.num_balloons
            for strategy in strategies:
                game_id = str(balloon_seed) + "_" + strategy.name
                game = Game([strategy], balloon_seed, game_id, num_balloons)
                Game_objects.append(game)

    return Game_objects

# Runs a game according to the config
# Returns the game_id of the game that it just ran
def run_game(game: Game, database_path: str, color_map: dict[str, float]) -> int:
    game_id = game.game_id 
    game.main(database_path, color_map)

    return game_id

# Converts table in SQL to csv for plotting
# Also writes a manifest beside each csv, see write_manifest()
def save_games(games: list[Game], database_path: str, game_log_path: str, raw_yaml: dict) -> None:
    conn = sqlite3.Connection(database_path)

    try:
        new_folder = os.path.join(game_log_path, raw_yaml["run_name"])
        Path(new_folder).mkdir(exist_ok = True)
        new_yaml = os.path.join(new_folder, "config.yaml")
        with open(new_yaml, "w") as f:
            yaml.safe_dump(raw_yaml, f, sort_keys=False, default_flow_style=False)
        for game in games:
            game_id = game.game_id
            game_log = pd.read_sql_query(f"SELECT * FROM game_{game_id}", conn)
            game_log.to_csv(os.path.join(new_folder, f"game_{game_id}_log.csv"), index = False)
    finally:
        conn.commit()
        conn.close()


# Writes the run settings that the csv itself cannot carry
# The colour probabilities are the important one: regret is measured against the
# optimal threshold for each colour, so without them a log cannot be scored later.
# game_id is not reliably parseable back into (seed, strategies) because strategy
# names contain underscores, so the manifest is the source of truth for both.
def make_manifest(game: Game, game_log_path: str, raw_yaml: dict) -> dict:
    manifest = {
        "game_id": game.game_id,
        "seed": int(game.seed),
        "num_balloons": int(game.num_balloons),
        "multiplayer": int(raw_yaml["multiplayer"]),
        "strategies": [strategy.name for strategy in game.strategies],
        "color_map": {str(color): float(p) for color, p in raw_yaml["color_map"].items()},
    }
    return manifest
    




# HELPER FUNCTIONS:

# Returns True if 
# 1. 0<p<1
# 2. at least one seed
# 3. if multiplayer == True, exactly 2 strategies
# 4. num_balloons >= 1
# 5. seeds are integers
# 6. multiplayer must be 1 or 0
def check_game_settings(raw_yaml: dict) -> bool:

    # 1. 
    for probability in raw_yaml["color_map"].values():
        if probability >= 1 or probability <= 0:
            raise ValueError("probabilities need to be between 0 and 1")

    # 2. 
    if raw_yaml["master_seed"] is None or raw_yaml["num_seeds"] < 1:
        raise ValueError("Please enter at least 1 seed")

    # 4. 
    if raw_yaml["num_balloons"] < 1:
        raise ValueError("number of balloons must be greater than 0")

    # 5.
    if not isinstance(raw_yaml["master_seed"], int) or not isinstance(raw_yaml["num_seeds"], int):
        raise ValueError("seeds must be integers (and number of seeds)")

    if raw_yaml["multiplayer"] != 0 and raw_yaml["multiplayer"] != 1:
        raise ValueError("Multiplayer mode takes value 0 or 1")
    
    return True

# Checks if strategies entered are in the registry
# This will raise a ValueError
def check_strat_names(raw_yaml: dict) -> bool:
    strategies = raw_yaml["strategies"]
    for strategy in strategies:
        if strategy["name"] not in Strategy.REGISTER:
            raise ValueError("This strategy does not exist")
    return True

# Checks if parameters given are in the correct format
def check_params(raw_yaml: dict) -> bool:
    strategies = raw_yaml["strategies"]
    num_strategies = len(strategies)
    for strategy in strategies:
        key = strategy["name"]
        cls = Strategy.REGISTER[key]
        num_params = len(strategy["params"])
        for given_param_attr, given_param_val in strategy["params"].items():

            for correct_param_attr, correct_param_type in cls.PARAMS:
                if given_param_attr == correct_param_attr:
                    if isinstance(given_param_val, correct_param_type):
                        num_params -= 1
                    else:
                        raise ValueError("parameter type wrong")

        if num_params == 0:
            num_strategies -= 1
        else:
            return False
    if num_strategies == 0:
        return True
    else:
        return False


# Instantiates strategies
# returns a list of strategy objects
def strat_instance(strategies: list[dict], strat_seeds: list[int], ctx: Context):
    strat_instances = []
    for strat in strategies:
        rng = np.random.default_rng(strat_seeds.pop())
        cls = Strategy.REGISTER[strat["name"]]
        strat_instances.append(cls(**strat["params"], ctx=ctx, rng=rng))

    return strat_instances
            

