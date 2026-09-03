import os
import sys



DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "db", "game_logs.db")
GAME_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "game_logs")
COLOR_MAP = {"red": 0.4, 
             "blue": 0.6, 
             "orange": 0.7, 
             "purple": 0.5}

YAML_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp.yaml")

class GameConfigs:
    def __init__(self, seed: int,  num_balloons: int, color_map: dict[str, float], strategies: list[str], multiplayer_mode: bool):
        self.seed = seed
        self.multiplayer = multiplayer_mode
        self.num_balloons = num_balloons
        self.color_map = color_map
        self.strategies = strategies









        
