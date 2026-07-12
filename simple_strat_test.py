
import pytest
from simple_strategies import explore_then_exploit
from Classes import Balloon
from Classes import Game
import sqlite3
import pandas as pd


@pytest.mark.exploit
def test_override():
    # Test if action of child class overrides parent method
    
    my_strat = explore_then_exploit(0.5, True, 100, "game_logs.db", 1)
    test_balloon = Balloon("yellow", 2, False, 0)
    move = my_strat.action(test_balloon)
    my_game = Game([my_strat], 100, 1, "game_logs.db")

    # Default parent action should cash since value >= 1
    assert move != "c"
    assert move == "p"

@pytest.mark.exploit
def test_unseen_handling():
    # Unseen balloons be pumped once and then cashed

    test_balloon  = Balloon("purple", 0, False, 0)
    my_strat = explore_then_exploit(0.5, True, 100, "game_logs.db", 1)

    move = my_strat.unseen_color_handling(test_balloon)
    assert move == "p"

    
    test_balloon2  = Balloon("purple", 1, False, 0)
    move2 = my_strat.unseen_color_handling(test_balloon2)
    assert move2 == "c"

@pytest.mark.sql
def test_num_pumps():
    
    test_strat = explore_then_exploit(0.5, True, 100, "game_logs.db", 1)
    test_game = Game([test_strat], 100, 1, "game_logs.db")
    conn = sqlite3.connect("game_logs.db")
    cur = conn.cursor()
    cur.execute('INSERT INTO game_1 VALUES (1, 2, "yellow", 1, "test_strat", "p", 1, 0, 0)')
    cur.execute('INSERT INTO game_1 VALUES (2, 2, "yellow", 9, "test_strat", "p", 1, 0, 0)')
    conn.commit()
    avg_lifespan = test_strat.num_pumps("yellow")
    assert avg_lifespan == 8
    cur.execute("DELETE FROM game_1")
    conn.commit()
    df = pd.read_sql_query("SELECT * FROM game_1", conn)
    print(df)

@pytest.mark.exploit
def test_action():
    test_strat = explore_then_exploit(0.25, True, 5, "game_logs.db", 1)
    test_game = Game([test_strat], 5, 1, "game_logs.db")
    conn = sqlite3.connect("game_logs.db")
    cur = conn.cursor()
    cur.execute('DELETE FROM game_1')

    conn.commit()    
    cur.execute('INSERT INTO game_1 VALUES (1, 1, "yellow", 1, "test_strat", "p", 1, 0, 0)')
    cur.execute('INSERT INTO game_1 VALUES (2, 1, "yellow", 2, "test_strat", "p", 1, 0, 0)')
    cur.execute('INSERT INTO game_1 VALUES (3, 1, "yellow", 3, "test_strat", "p", 1, 0, 0)')

    conn.commit()

    test_balloon = Balloon("yellow", 20, True, 0)
    move = test_strat.action(test_balloon)

    # TEST 1: phase cutoff
    # Since we are still in exploration phase it should always pump (1/5 < 0.25)
    assert move == "p"

    cur.execute('INSERT INTO game_1 VALUES (4, 2, "blue", 1, "test_strat", "p", 1, 0, 0)')
    cur.execute('INSERT INTO game_1 VALUES (5, 2, "blue", 2, "test_strat", "p", 1, 0, 0)')
    cur.execute('INSERT INTO game_1 VALUES (6, 2, "blue", 3, "test_strat", "p", 1, 0, 0)')
    cur.execute('INSERT INTO game_1 VALUES (7, 3, "blue", 4, "test_strat", "p", 1, 0, 0)')

    conn.commit()
    test_balloon2 = Balloon("purple", 1, True, 0)
    test_balloon3 = Balloon("blue", 1, False, 0)
    # we haven't seen purple before -> should use unseen_handling
    
    # TEST 2: check if unseen balloon colors are being handled correctly
    move = test_strat.action(test_balloon2)
    assert move == "c"

    # TEST 3: check if averages are being calculated correctly
    move = test_strat.action(test_balloon3)
    assert move == "p"


    cur.execute('DELETE FROM game_1')
    conn.commit()


