

from config import GameConfigs
from engine import Game
from strategies import Strategy
import yaml

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
def parse_inputs(yaml_path: str) -> GameConfigs:

    with open(yaml_path) as f:
        raw_yaml = yaml.safe_load(f)

    # 1. Check if strategy names are in register
    valid_strategies = check_strat_names(raw_yaml)

    # 2. Check if parameters are correct type
    valid_parameters = check_params(raw_yaml)

    # 3. Check game settings
    valid_game_settings = check_game_settings(raw_yaml)

    if all(valid_game_settings, valid_parameters, valid_strategies):
        return raw_yaml

# Builds the correct games from a GameConfigs object
def build_games(raw_yaml: dict) -> list[Game]:
    # Sort strategies 



    # Generate seeds for balloons for each game 



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
            return True
        else:
            return False


