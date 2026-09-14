
import os
import pandas as pd
import numpy as np
from paths import GAME_LOG_PATH
import json
from pathlib import Path
import re

# function that computes the realized cumulative regret 
# and puts it as a column in the dataframe
# input is raw dataframe from csv doc
# Only use in singleplayer mode
def add_regret(df:pd.DataFrame, raw_yaml: dict) -> pd.DataFrame:
    df = df.copy()
    color_map = raw_yaml["color_map"]
    df["p"] = df["balloon_color"].map(color_map)
    df["oracle_threshold"] = np.ceil((1-df["p"])/df["p"]).map(int)
    df["oracle_popped"] = df["oracle_threshold"] >= df["pop_time"]
    df["oracle_gain"] = (1-df["oracle_popped"].map(int))*df["oracle_threshold"]
    df["oracle_pnl"] = df["oracle_gain"].cumsum()
    df["regret"] = df["oracle_pnl"] - df["end_PnL"]

    return df["regret"]

# Function that averages a certain parameter/column over all the seeds 
# this is done per balloon 
# and added as a new column
# resulting df should have 3 columns: Strategy_name, balloon_id, avg_val of param
def avg_over_seeds(combined_df: pd.DataFrame, parameter: str) -> pd.DataFrame:
    summary = combined_df.groupby(["strategy_name", "balloon_id"]).agg(**{parameter: (parameter, "mean")}).reset_index()
    return summary








    



