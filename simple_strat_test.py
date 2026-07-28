
import pytest
from simple_strategies import explore_then_exploit, constant_pump
from Classes import Balloon
from Classes import Game
import sqlite3
import pandas as pd
from config import DATABASE_PATH, COLOR_MAP


# Tests if action of child class overrides parent method
@pytest.mark.exploit
def test_override():
    Game.clear_game(1)
    my_strat = explore_then_exploit(0.5, 100, 1, 1)
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
    my_strat = explore_then_exploit(0.5, 100, 1, 1)

    move = my_strat.unseen_color_handling(test_balloon)
    assert move == "p"

    
    test_balloon2  = Balloon("purple", 1, False, 0)
    move2 = my_strat.unseen_color_handling(test_balloon2)
    assert move2 == "c"

    Game.clear_game(1)


@pytest.mark.exploit
def test_num_pumps():
    conn = sqlite3.Connection(DATABASE_PATH)
    cur = conn.cursor()

    Game.clear_game(1)

    test_strat = explore_then_exploit(0.8, 100, 1, 1)
    test_strat2 = explore_then_exploit(0.8, 100, 1, 2)

    # TEST 1: Correct output for single player
    def insert_balloon(balloon_num: int, color: str, max_val, name: str):
        for i in range(max_val+1):
            cur.execute('INSERT INTO game_1 VALUES (0, ?, ?, ?, ?, "p", 0, 0, 0)', (balloon_num, color, i, name))

    insert_balloon(1, "yellow", 8, "explore_exploit_1")
    insert_balloon(2, "yellow", 6, "explore_exploit_1")
    insert_balloon(3, "yellow", 5, "explore_exploit_1")
    insert_balloon(4, "yellow", 4, "explore_exploit_1")
    insert_balloon(5, "yellow", 3, "explore_exploit_1")
    insert_balloon(6, "yellow", 5, "explore_exploit_1")
    insert_balloon(7, "yellow", 8, "explore_exploit_1")
    insert_balloon(8, "yellow", 6, "explore_exploit_1")
    insert_balloon(9, "red", 5, "explore_exploit_1")
    insert_balloon(10, "red", 4, "explore_exploit_1")
    insert_balloon(11, "red", 3, "explore_exploit_1")
    insert_balloon(12, "red", 5, "explore_exploit_1")
    insert_balloon(13, "blue", 8, "explore_exploit_1")
    insert_balloon(14, "blue", 6, "explore_exploit_1")
    insert_balloon(15, "blue", 5, "explore_exploit_1")
    insert_balloon(16, "blue", 4, "explore_exploit_1")
    insert_balloon(17, "blue", 3, "explore_exploit_1")
    insert_balloon(18, "blue", 10, "explore_exploit_1")

    conn.commit()

    yellow_avg = 5.625
    red_avg = 4.25
    blue_avg = 6

    assert yellow_avg == pytest.approx(test_strat.num_pumps("yellow"))
    assert red_avg == pytest.approx(test_strat.num_pumps("red"))
    assert blue_avg == pytest.approx(test_strat.num_pumps("blue"))

    # TEST 2: Correct output for multiplayer too
    insert_balloon(1, "yellow", 8, "explore_exploit_2")
    insert_balloon(2, "yellow", 4, "explore_exploit_2")
    insert_balloon(3, "yellow", 2, "explore_exploit_2")
    insert_balloon(4, "yellow", 5, "explore_exploit_2")
    insert_balloon(5, "yellow", 10, "explore_exploit_2")
    insert_balloon(6, "yellow", 5, "explore_exploit_2")
    insert_balloon(7, "yellow", 8, "explore_exploit_2")
    insert_balloon(8, "yellow", 6, "explore_exploit_2")
    insert_balloon(9, "red", 15, "explore_exploit_2")
    insert_balloon(10, "red", 23, "explore_exploit_2")
    insert_balloon(11, "red", 18, "explore_exploit_2")
    insert_balloon(12, "red", 8, "explore_exploit_2")
    insert_balloon(13, "blue", 8, "explore_exploit_2")
    insert_balloon(14, "blue", 11, "explore_exploit_2")
    insert_balloon(15, "blue", 12, "explore_exploit_2")
    insert_balloon(16, "blue", 9, "explore_exploit_2")
    insert_balloon(17, "blue", 1, "explore_exploit_2")
    insert_balloon(18, "blue", 10, "explore_exploit_2")

    conn.commit()

    yellow_avg2 = 6
    red_avg2 = 16
    blue_avg2 = 8.5

    assert yellow_avg2 == pytest.approx(test_strat2.num_pumps("yellow"))
    assert red_avg2 == pytest.approx(test_strat2.num_pumps("red"))
    assert blue_avg2 == pytest.approx(test_strat2.num_pumps("blue"))


    # Clean table
    Game.clear_game(1)
    conn.close()



    
    
    

    
    


    





