

import pandas as pd

import matplotlib.pyplot as plt

df = pd.read_csv("game_logs/game_5_log")


df_constant_pump = df[df["strategy_name"] == "Constant_pump_4"].groupby("balloon_number", as_index=False)["player_PnL"].first()
df_explore_exploit = df[df["strategy_name"] == "explore_exploit_1"].groupby("balloon_number", as_index=False)["player_PnL"].first()
df_thompson = df[df["strategy_name"] == "thompson_sampling"].groupby("balloon_number", as_index=False)["player_PnL"].first()

x = df_constant_pump["balloon_number"]
y1 = df_constant_pump["player_PnL"]
y2 = df_explore_exploit["player_PnL"]
y3 = df_thompson["player_PnL"]

plt.plot(x, y1, label = "constant_pump", color = "blue")
plt.plot(x, y2, label = "explore_exploit", color = "red")
plt.plot(x, y3, label = "thompson_sampling", color = "orange")
plt.xlabel("balloon_number")
plt.ylabel("PnL")
plt.legend()


plt.show()







