


from strategies import thompson_sampling, constant_pump, explore_exploit, oracle
from engine import Game
from sql_handling import SQL_handling
import sqlite3
from config import DATABASE_PATH, GAME_LOG_PATH
import pandas as pd
import os

seed = 102301
num_balloons = 1000
def convert_csv(folder_path: str, game_id: int, conn: sqlite3.Connection) -> None:
    game_log = pd.read_sql_query(f"SELECT * FROM game_{game_id}", conn)
    game_log.to_csv(os.path.join(folder_path, f"game_{game_id}_log.csv"), index = False)

test_strat1 = thompson_sampling()
test_strat2 = constant_pump(3)
test_strat3 = explore_exploit(0.1, num_balloons)
test_strat4 = oracle()



test_game_1 = Game([test_strat1], seed, 1, num_balloons)
test_game_2 = Game([test_strat2], seed, 2, num_balloons)
test_game_3 = Game([test_strat3], seed, 3, num_balloons)
test_game_4 = Game([test_strat4], seed, 4, num_balloons)


test_game_1.main()
test_game_2.main()
test_game_3.main()
test_game_4.main()

conn = sqlite3.Connection(DATABASE_PATH)
convert_csv(GAME_LOG_PATH, 1, conn)
convert_csv(GAME_LOG_PATH, 2, conn)
convert_csv(GAME_LOG_PATH, 3, conn)
convert_csv(GAME_LOG_PATH, 4, conn)



import matplotlib.pyplot as plt

df_constant_pump = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_2_log.csv"))
df_thompson = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_1_log.csv"))
df_explore_exploit = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_3_log.csv"))
df_benchmark = pd.read_csv(os.path.join(GAME_LOG_PATH, "game_4_log.csv"))

x = df_constant_pump["balloon_id"]
y1 = df_benchmark["end_PnL"] - df_constant_pump["end_PnL"]
y2 =  df_benchmark["end_PnL"] - df_explore_exploit["end_PnL"]
y3 = df_benchmark["end_PnL"] - df_thompson["end_PnL"]


plt.plot(x, y1, label = "constant_pump", color = "blue")
plt.plot(x, y2, label = "explore_exploit", color = "red")
plt.plot(x, y3, label = "thompson_sampling", color = "orange")

plt.xlabel("balloon_number")
plt.ylabel("Regret")
plt.legend()


plt.show()


