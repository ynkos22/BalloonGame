
from Classes import Balloon, Player, Game
import pytest
from IPython.display import display

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