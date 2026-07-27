
import pytest
from simple_strategies import explore_then_exploit, constant_pump
from Classes import Balloon
from Classes import Game
import sqlite3
import pandas as pd
from config import DATABASE_PATH


# Tests if action of child class overrides parent method
@pytest.mark.exploit
def test_override():
    Game.clear_game(1)
    my_strat = explore_then_exploit(0.5, 100, 1)
    test_balloon = Balloon("yellow", 2, False, 0)
    move = my_strat.action(test_balloon)
    
    # Default parent action should cash since value >= 1
    assert move != "c"
    assert move == "p"

# Tests if balloons of unseen colors are handled correctly
@pytest.mark.exploit
def test_unseen_handling():
    # Unseen balloons be pumped once and then cashed

    test_balloon  = Balloon("purple", 0, False, 0)
    my_strat = explore_then_exploit(0.5, 100, 1)

    move = my_strat.unseen_color_handling(test_balloon)
    assert move == "p"

    
    test_balloon2  = Balloon("purple", 1, False, 0)
    move2 = my_strat.unseen_color_handling(test_balloon2)
    assert move2 == "c"

    Game.clear_game(1)


@pytest.mark.exploit
def test_num_pumps():
    conn = sqlite3.Connection(DATABASE_PATH)
    Game.clear_game(1)

    # Before we test anything we need to generate some data
    data_prod_strat = constant_pump(5)
    test_game = Game([data_prod_strat], 20, 1)

    df = pd.read_sql_query("SELECT * FROM game_1", conn)
    aggregated_df = df.groupby("balloon_color")["balloon_value"].max()
    


    





