
import os
import pandas as pd
import numpy as np
from paths import GAME_LOG_PATH
import json


# function that computes the realized cumulative regret 
# and puts it as a column in the dataframe
# input is raw dataframe from csv doc
# Only use in singleplayer mode
def add_regret(df:pd.DataFrame, manifest: dict) -> pd.DataFrame:
    df = df.copy()
    color_map = manifest["color_map"]
    df["p"] = df["balloon_color"].map(color_map)
    df["oracle_threshold"] = np.ceil((1-df["p"])/df["p"]).map(int)
    df["oracle_popped"] = df["oracle_threshold"] >= df["pop_time"]
    df["oracle_gain"] = (1-df["oracle_popped"].map(int))*df["oracle_threshold"]
    df["oracle_pnl"] = df["oracle_gain"].cumsum()
    df["regret"] = df["oracle_pnl"] - df["end_PnL"]

    df = df.drop(columns=["p", "oracle_threshold", "oracle_popped", "oracle_pnl"])

    return df

# function that takes the average of strategy performance over many seeds






    



