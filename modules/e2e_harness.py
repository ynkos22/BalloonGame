

from config import GameConfigs
from engine import Game
from strategies import Strategy
import yaml

# Checks if the user's yaml document contains valid data
# returns GameConfigs object used in build_games()
def parse_inputs(raw_yaml: dict) -> GameConfigs:
    pass

# Builds the correct games from a GameConfigs object
def build_games(config: GameConfigs) -> list[Game]:
    pass

# Runs a game according to the config
def run_game(game: Game) -> None:
    pass

# Converts table in SQL to csv for plotting
def save_game(game_id: int) -> None:
    pass



# HELPER FUNCTIONS:

# Returns True if 
# 1. 0<p<1
# 2. at least one seed
# 3. if multiplayer == True, exactly 2 strategies
# 4. num_balloons >= 1
# 5. seeds are integers
# 6. if round robin mode is True, then multiplayer mode is also true
def check_game_settings(raw_yaml: dict) -> bool:
    pass

# Checks if strategies entered are in the registry
# This will raise a ValueError
def check_strat_names() -> bool:
    pass

# Checks if parameters given are in the correct format
def check_params() -> bool:
    pass

# Get the object from the name of a strategy
def get_strat_obj(strat_name: str):
    pass

# Returns the GameConfig object from the necessary information
# input dict is raw dict from .yaml parsing
def make_obj(input: dict, strategies: list[Strategy]):

    seeds = input["seeds"]
    num_balloons = input["num_balloons"]
    multiplayer_mode = input["multiplayer_mode"]
    color_map = input["color_map"]

    obj = GameConfigs(seeds, num_balloons, color_map, strategies, multiplayer_mode)
    
    return obj


