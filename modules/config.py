import os
import sys
from strategies import Strategy


DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "db", "game_logs.db")
GAME_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "game_logs")
COLOR_MAP = {"red": 0.4, 
             "blue": 0.6, 
             "orange": 0.7, 
             "purple": 0.5}



class GameConfig:
    def __init__(self, seeds: list[int],  num_balloons: int, color_map: dict[str, float], strategies: list[Strategy]):
        self.seeds = seeds
        self.num_balloons = num_balloons
        self.color_map = color_map
        self.strategies = strategies









        
