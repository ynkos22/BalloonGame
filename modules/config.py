import os
import sys

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "db", "game_logs.db")
GAME_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "game_logs")
COLOR_MAP = {"red": 0.4, 
             "blue": 0.6, 
             "orange": 0.7, 
             "purple": 0.5}