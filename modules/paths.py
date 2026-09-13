import os

# Project paths, kept in their own module so that importing them does not pull in
# config.py (which runs an experiment on import).

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_PATH = os.path.join(ROOT, "output", "db", "game_logs.db")
GAME_LOG_PATH = os.path.join(ROOT, "output", "game_logs")
PLOT_PATH = os.path.join(ROOT, "output", "plots")
YAML_FILE_PATH = os.path.join(ROOT, "config.yaml")
