from Classes import Balloon, Player, Game
from simple_strategies import constant_pump, explore_then_exploit
import pandas as pd

player2_memory = [pd.DataFrame(columns=["color", "pumps"]), [0.5]]  # Initialize memory for explore_then_exploit strategy

Player1 = Player(constant_pump, 1, 0, 0, [None, [5]])

Player2 = Player(explore_then_exploit, 2, 0, 0, player2_memory)

testGame = Game([Player1, Player2], 100, 1)

testGame.start()




