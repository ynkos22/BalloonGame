


from strategies import thompson_sampling, constant_pump, explore_exploit, oracle
from engine import Game
from sql_handling import SQL_handling
import sqlite3
from config import DATABASE_PATH, GAME_LOG_PATH
import pandas as pd
import os
from strategies import Strategy


def convert_csv(folder_path: str, game_id: int, conn: sqlite3.Connection) -> None:
    game_log = pd.read_sql_query(f"SELECT * FROM game_{game_id}", conn)
    game_log.to_csv(os.path.join(folder_path, f"game_{game_id}_log.csv"), index = False)

def run_games(strategies: list[Strategy], seed: int, num_balloons: int, start_game_id: int):
    for i in range(start_game_id, start_game_id + len(strategies)):
        game = Game([strategies[i-start_game_id]], seed, i, num_balloons)
        game.main()
        strategies[i-start_game_id].PnL = 0

    # Convert to csv
    conn = sqlite3.Connection(DATABASE_PATH)
    for i in range(start_game_id, start_game_id + len(strategies)):
        convert_csv(GAME_LOG_PATH, i, conn)
    conn.commit()
    conn.close()



seed = 102301
num_balloons = 1000

test_strat1 = thompson_sampling()
test_strat2 = constant_pump(3)
test_strat3 = explore_exploit(0.1, num_balloons)
test_strat4 = oracle()

strats = [test_strat1, test_strat2, test_strat3, test_strat4]


run_games(strats, seed, num_balloons, 6)

"""

import matplotlib.pyplot as plt

df_constant_pump = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_2_log.csv"))
df_thompson = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_1_log.csv"))
df_explore_exploit = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_3_log.csv"))
df_benchmark = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_4_log.csv"))

x = df_constant_pump["balloon_id"]
y1 = df_benchmark["end_PnL"] - df_constant_pump["end_PnL"]
y2 =  df_benchmark["end_PnL"] - df_explore_exploit["end_PnL"]
y3 = df_benchmark["end_PnL"] - df_thompson["end_PnL"]

df_duel = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_5_log.csv"))
df_x = df_duel[df_duel["strategy_name"] == "explore_exploit_0.1"]
df_t = df_duel[df_duel["strategy_name"] == "thompson_sampling"]

y4 = df_x["end_PnL"]
y5 = df_t["end_PnL"]

plt.plot(x, y4, label = "explore_exploit", color = "blue")
plt.plot(x, y5, label = "thompson", color = "red")

plt.xlabel("balloon_number")
plt.ylabel("PnL")
plt.legend()


plt.plot(x, y1, label = "constant_pump", color = "blue")
plt.plot(x, y2, label = "explore_exploit", color = "red")
plt.plot(x, y3, label = "thompson_sampling", color = "orange")

plt.xlabel("balloon_number")
plt.ylabel("Regret")
plt.legend()


plt.show()

"""
