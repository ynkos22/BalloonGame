import pandas as pd
from Classes import Balloon, Strategy, Game
import pytest
from IPython.display import display
import sqlite3


@pytest.mark.balloon
def test_popping_inflation():

    testBalloon = Balloon("yellow", 0, False)

    testBalloon.inflate()
    print(f"Balloon value: {testBalloon.value}, popped: {testBalloon.popped}")
    assert testBalloon.value == 1
    assert testBalloon.popped == False

@pytest.mark.player
def test_pnl_calculation():
    def test_strategy(balloon):
        if balloon.value == 0:
            return "p"
        else:
            return "c"

    testPlayer = Player(test_strategy, 1, 0, 0)
    testBalloon = Balloon("red", 0, False, 0)
    # Test if player inflates balloon and updates unrPnL correctly
    testPlayer.action(testBalloon)
    assert testPlayer.unrPnL == 1
    
    # Test if player cashes out and updates PnL correctly
    testPlayer.action(testBalloon)
    assert testPlayer.PnL == 1
    # Test if popping mechanism works correctly
    testBalloon = Balloon("blue", 0, False, 1)  # Set probability to 1 for guaranteed pop
    testPlayer.action(testBalloon)
    assert testBalloon.popped == True
    assert testBalloon.value == 0
    assert testPlayer.unrPnL == 0  # unrPnL should reset to 0 after popping
    assert testPlayer.PnL == 1  # PnL should remain unchanged after popping


@pytest.mark.game
def test_game_log():
    def test_strategy(balloon):
        if balloon.value < 2:
            return "p"
        else:
            return "c"

    testPlayer = Player(test_strategy, 1, 0, 0)
    testGame = Game([testPlayer], 100, 3)
    game_log = testGame.start()
    display(game_log)
    assert all(game_log["balloon_value"] >= 0)
    assert len(game_log) > 0
    assert min(game_log["balloon_value"]) >= 0
    assert min(game_log["player_PnL"]) >= 0
    assert min(game_log["player_unrPnL"]) >= 0

@pytest.mark.game
def test_game_summary():

    def test_strategy(balloon):
        if balloon.value < 2:
            return "p"
        else:
            return "c"

    testPlayer = Player(test_strategy, 1, 0, 0)
    testGame = Game([testPlayer], 100, 3)
    game_log = testGame.start()
    testGame.print_summary(game_log)

@pytest.mark.game
def test_balloon_reset():
    balloon1 = Balloon("yellow", 3, True)
    balloon2 = Balloon("red", 3, True)
    balloon3 = Balloon("blue", 2, True)
    balloons = [balloon1, balloon2, balloon3]
    Game.reset_balloons(balloons)
    assert all(not balloon.popped for balloon in balloons)
    assert all(balloon.value == 0 for balloon in balloons)


@pytest.mark.game
def test_turn_loop():
    def always_pump_strategy(balloon, memory=None):
        return "p"

    balloon1 = Balloon("yellow", 3, False)
    balloon2 = Balloon("red", 2, False)
    balloons = [balloon1, balloon2]

    testPlayer = Player(always_pump_strategy, 1, 0, 0, None)
    testGame = Game([testPlayer], 100, 3)

    log, action = testGame.per_turn_game_loop(balloons[0], 6, 2, testPlayer)

    assert log["balloon_value"] == 3
    assert log["turn"] == 3
    assert log["balloon_number"] == 7
    assert action == "p"

@pytest.mark.game
def test_balloon_loop():
    def always_pump_strategy(balloon, memory=None):
        return "p"
    def always_cash_strategy(balloon, memory=None):
        return "c"
    balloon1 = Balloon("yellow", 3, False)
    balloon2 = Balloon("red", 2, False)
    balloons = [balloon1, balloon2]

    testPlayer = Player(always_pump_strategy, 1, 0, 0, None)
    testPlayer2 = Player(always_cash_strategy, 2, 0, 0, None)
    testGame = Game([testPlayer, testPlayer2], 100, 3)

    initial_log = pd.DataFrame(columns=["turn", "balloon_number", "balloon_color", "balloon_value", "player_id", "player_action", "popped", "player_unrPnL", "player_PnL"])
    initial_log2 = pd.DataFrame(columns=["turn", "balloon_number", "balloon_color", "balloon_value", "player_id", "player_action", "popped", "player_unrPnL", "player_PnL"])
    game_log, current_turn = testGame.per_balloon_game_loop(balloons, 0, 0, testPlayer, initial_log)
    game_log2, current_turn2 = testGame.per_balloon_game_loop(balloons, 1, 0, testPlayer2, initial_log2)
    assert current_turn >= 1
    assert current_turn == len(game_log)
    assert len(game_log2) == 1
    assert all([action == "c" for action in game_log2["player_action"]])

@pytest.mark.sql
def test_sql_init():
    test_strat = Strategy("test_strat", 0, 0, "game_logs.db")
    test_game = Game([test_strat], 100, 1, "game_logs.db")

    df = pd.read_sql_query("SELECT * FROM game_1", test_game.conn)
    # Make sure columns are correct
    assert list(df.columns) == ["turn", 
                        "balloon_number", 
                        "balloon_color", 
                        "balloon_value", 
                        "strategy_name", 
                        "player_action", 
                        "popped", 
                        "player_unrPnL", 
                        "player_PnL"]
    # Make sure there are no entries yet
    assert len(df) == 0


@pytest.mark.summary
def test_summary():
    conn = sqlite3.Connection("game_logs.db")
    cur = conn.cursor()
    df = pd.read_sql_query("SELECT * FROM game_1", conn)
    
    # format expected: turn, balloon_number, balloon_color, balloon_value, strategy_name, player_action, popped, player_unrPnL, player_PnL
    assert len(df) == 0 # make sure the table is empty

    cur.execute('INSERT INTO game_1 VALUES (1, 2, "R", 3, "test_strat", "p", 1, 0, 0)')
    conn.commit()
    df = pd.read_sql_query("SELECT * FROM game_1", conn)
    assert len(df) == 1

    Game.print_summary(1)

    try:
        df = pd.read_csv("game_logs/game_1_log")
        assert len(df) == 1
        assert list(df.iloc[0]) == [1, 2, "R", 3, "test_strat", "p", 1, 0, 0]
    except FileNotFoundError:
        print("can't find file")

    # reverse the changes for testing purposes
    cur.execute("DELETE FROM game_1")
    conn.commit()




    


    

    
    
   



