

from config import GameConfig
from engine import Game
from strategies import Strategy



# Checks if the user's yaml document contains valid data
def valid_game_input(raw_yaml: dict):
    pass

# Get the object from the name of a strategy
def get_strat_obj(strat_name: str):
    pass

# Inputs a list of strategy names
# Returns a list of the objects
def get_strat_list(strat_name_list: str):
    pass

# Parses a .yaml file and returns the correct Config objects for each seed
def yaml_parser(file_path: str) -> GameConfig:
    pass

# Returns the GameConfig object from the necessary information
def make_obj(input: dict, strategies: list[Strategy]):
    pass

# Builds the correct game from a GameConfig object
def build_game(config: GameConfig) -> Game:
    pass

# Runs a game according to the config
def run_game(game: Game):
    pass


# Converts table in SQL to csv for plotting
def convert_csv(game_id: int):
    pass

# Everyone faces everyone over all the seeds
def round_robin(config: GameConfig):
    pass

# Returns the expected payout of a strategy (in ONE turn) 
# by quoting threshold on a balloon with pop prob true_p
# Used to calculate and plot pseudo regret
def expected_payout(threshold: int, true_p: float):
    pass