
from matplotlib import pyplot as plt
import pandas as pd
from paths import GAME_LOG_PATH
import json
import os
from pathlib import Path
import yaml
import re
from metrics import add_regret, avg_over_seeds

# Function that goes througha folder and converts all the csv docs
# into Dataframes and returns a list

def csv_to_df(folder_name: str) -> list[pd.DataFrame]:
    dfs = []
    folder_path  = os.path.join(GAME_LOG_PATH, folder_name)
    for p in Path(folder_path).glob("game_*_log.csv"):
        dfs.append(pd.read_csv(p))
    return dfs

# Function that adds a new column
# computed from other columns or constants (a function)

def add_column(df: pd.DataFrame, f, column_name: str) -> pd.DataFrame:
    df[column_name] = f(df)
    return df

# Function that combines many dataframes (with the same columns)
# into a combined df
def combine_df(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


# Function that separates a strategy from the others in a df
def separate_strat(df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
    try:
        df = df[df["strategy_name"] == strategy_name]
    finally:
        return df

# Function that takes in a list of dfs, a list of labels, plot_title, and a parameter
# plots this parameter against balloon_id for all the dfs
def plot_dfs(dfs: list[pd.DataFrame], labels: list[str], plot_title: str, parameter: str) -> None:
    f = lambda x: x[parameter]
    x = dfs[0]["balloon_id"]
    ys = list(map(f, dfs))
    mult_y_plot(x, ys, y_labels=labels, plot_title=plot_title)
    

# Function that plots multiple y over the same x
def mult_y_plot(x: list, ys: list[list], y_labels: list[str], plot_title: str) -> None:

    for i in range(len(ys)):
        plt.plot(x, ys[i], label=y_labels[i])

    plt.title(plot_title)  
    plt.legend()
    plt.show()



# Function that reads yaml file
# Returns dictionary
def read_yaml(filename: str) -> dict:
    with open(filename) as f:
        raw_yaml = yaml.safe_load(f)
    return raw_yaml




# MIXED FUNCTIONS



def plot_curves(run_name: str, y_var: str, function, plot_title: str) -> None:

    dfs = csv_to_df(run_name)
    yaml_dict = read_yaml(os.path.join(GAME_LOG_PATH, run_name, "config.yaml"))
    
    f = lambda x: function(x, yaml_dict)
    for df in dfs:
        add_column(df, f, y_var)

    combined_df = combine_df(dfs)
    avg_df = avg_over_seeds(combined_df, y_var)
    strat_names = combined_df["strategy_name"].unique()
    strat_dfs = list(map(lambda y: separate_strat(avg_df, y), strat_names))

    plot_dfs(strat_dfs, strat_names, plot_title, y_var)


def plot_regret_curves(run_name: str) -> None:

    plot_curves(run_name, "regret", add_regret, "Cumulative Regret")

def plot_PnL_curves(run_name: str) -> None:

    plot_curves(run_name, "end_PnL", lambda x, y: x["end_PnL"], "Cumulative PnL")

