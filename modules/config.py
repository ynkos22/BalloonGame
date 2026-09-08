import os
import sys
from e2e_harness import parse_inputs, build_games, save_games, run_game
import yaml

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "db", "game_logs.db")
GAME_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "game_logs")
YAML_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")


# Running an experiment
def experiment(yaml_path: str) -> None:
    
    raw_yaml_dict = parse_inputs(yaml_path)
    color_map = raw_yaml_dict["color_map"]
    games = build_games(raw_yaml_dict)

    game_ids = []
    while len(games) != 0:
        game = games.pop()
        game_ids.append(run_game(game, DATABASE_PATH, color_map))

    save_games(game_ids, DATABASE_PATH, GAME_LOG_PATH)

experiment(YAML_FILE_PATH)




