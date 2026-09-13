from e2e_harness import parse_inputs, build_games, save_games, run_game
from paths import DATABASE_PATH, GAME_LOG_PATH, YAML_FILE_PATH


# Running an experiment
def experiment(yaml_path: str) -> None:

    raw_yaml_dict = parse_inputs(yaml_path)
    color_map = raw_yaml_dict["color_map"]
    games = build_games(raw_yaml_dict)

    for game in games:
        run_game(game, DATABASE_PATH, color_map)

    save_games(games, DATABASE_PATH, GAME_LOG_PATH, raw_yaml_dict)


if __name__ == "__main__":
    experiment(YAML_FILE_PATH)
