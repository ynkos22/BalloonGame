
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
    testBalloon = Balloon("red", 0, False)

    testPlayer.action(testBalloon)
    print(f"Player unrPnL: {testPlayer.unrPnL}, PnL: {testPlayer.PnL}")
    assert testPlayer.unrPnL == 1
    assert testPlayer.PnL == 0
    testPlayer.action(testBalloon)  # Inflate again
    print(f"Player unrPnL: {testPlayer.unrPnL}, PnL: {testPlayer.PnL}")
    assert testPlayer.unrPnL == 0
    assert testPlayer.PnL == 1


@pytest.mark.game
def test_game_log():
    def test_strategy(balloon):
        if balloon.value < 2:
            return "p"
        else:
            return "c"

    testPlayer = Player(test_strategy, 1, 0, 0)
    testGame = Game([testPlayer], 10)
    game_log = testGame.start()
    display(game_log)
    assert all(game_log["balloon_value"] >= 0)
    assert len(game_log) > 0
    assert min(game_log["balloon_value"]) >= 0
    assert min(game_log["player_PnL"]) >= 0
    assert min(game_log["player_unrPnL"]) >= 0

