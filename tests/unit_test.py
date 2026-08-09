import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules"))

from core import Balloon, Observation
from engine import Game
from strategies import Strategy
from config import COLOR_MAP



# TESTS FOR ENGINE

test_balloon = Balloon("red", 5, 0.2, 45)
test_strat1 = Strategy("test_strat1")
test_strat2 = Strategy("test_strat2")
test_game = Game([test_strat1, test_strat2], 1001, 1, 100)

@pytest.mark.engine
def test_calc_payout():
    # Both popped:
    threshold_1 = 6
    threshold_2 = 7
    thresholds = {
        test_strat1.name: threshold_1, 
        test_strat2.name: threshold_2
    }
    assert test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 0, 
                                                               test_strat2.name: 0}

    # strat1 pops, strat2 doesn't
    threshold_1 = 7
    threshold_2 = 3
    thresholds = {
            test_strat1.name: threshold_1, 
            test_strat2.name: threshold_2
        }

    assert test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 0, 
                                                               test_strat2.name: 3}

    # both don't pop, higher one wins all
    threshold_1 = 2
    threshold_2 = 3
    thresholds = {
                test_strat1.name: threshold_1, 
                test_strat2.name: threshold_2
            }
    assert test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 0, 
                                                                test_strat2.name: 5}
    threshold_1 = 4
    threshold_2 = 3
    thresholds = {
                test_strat1.name: threshold_1, 
                test_strat2.name: threshold_2
            }
    assert test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 7, 
                                                                test_strat2.name: 0}


    # Test what happens they tie (one of them wins by a fair coin flip)
    threshold_1 = 3
    threshold_2 = 3
    thresholds = {
                test_strat1.name: threshold_1, 
                test_strat2.name: threshold_2
            }
    
    assert test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 6, 
                                                                test_strat2.name: 0} or test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 0, 
                                                                test_strat2.name: 6}
    # Test if someone someone's threshold is EXACTLY pop_value
    threshold_1 = 5
    threshold_2 = 3
    thresholds = {
                test_strat1.name: threshold_1, 
                test_strat2.name: threshold_2
            }
    assert test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 0, 
                                                                test_strat2.name: 3}
    
    # Test if single player works
    threshold_1 = 3
    thresholds = {
                test_strat1.name: threshold_1
            }
    assert test_game.calc_payout(thresholds, test_balloon) == {test_strat1.name: 3}

@pytest.mark.engine
def test_update_PnL():
    payout = {test_strat1.name: 10,
              test_strat2.name: 0}

    PnL_dict = test_game.update_PnL([test_strat1, test_strat2], payout)

    assert test_strat1.PnL == 10 and test_strat2.PnL == 0

    payout = {test_strat1.name: 0,
                  test_strat2.name: 4}

    PnL_dict = test_game.update_PnL([test_strat1, test_strat2], payout)
    assert test_strat1.PnL == 10 and test_strat2.PnL == 4

    assert PnL_dict[test_strat1.name] == 10 and PnL_dict[test_strat2.name] == 4

    test_strat1.PnL = 0
    test_strat2.PnL = 0

    # Test what happens if payout and strategies don't match (should be automatically set to 0)
    payout = {test_strat1.name: 10}
    PnL_dict = test_game.update_PnL([test_strat1, test_strat2], payout)
    assert PnL_dict == {test_strat1.name: 10, test_strat2.name: 0}


    test_strat1.PnL = 0
    test_strat2.PnL = 0


    payout = {test_strat1.name: 10, 
              test_strat2.name: 20}
    PnL_dict = test_game.update_PnL([test_strat1], payout)
    assert PnL_dict[test_strat1.name] == 10

    test_strat1.PnL = 0
    test_strat2.PnL = 0

    # Test what happens with no strategies
    PnL_dict = test_game.update_PnL([], payout)
    assert PnL_dict == {}

    # Reset
    test_strat1.PnL = 0
    test_strat2.PnL = 0


@pytest.mark.engine
def test_obs_parser():
    payout = {
        test_strat1.name: 30,
        test_strat2.name: 0
    }
    thresholds = {
        test_strat1.name: 3,
        test_strat2.name: 4
    }
    result = test_game.obs_parser(thresholds, payout, test_balloon)

    obs1 = result[test_strat1.name]
    obs2 = result[test_strat2.name]

    assert obs1.own_threshold == 3 and obs2.own_threshold == 4
    assert obs1.balloon_color == "red" and obs2.balloon_color == "red"
    assert obs1.payout == payout and obs2.payout == payout
    assert isinstance(obs1, Observation) and isinstance(obs2, Observation)
    assert isinstance(result, dict)
    assert result.keys() == thresholds.keys()
    assert len(result.keys()) == 2

@pytest.mark.engine
def test_sql_parser():
    thresholds = {
            test_strat1.name: 3,
            test_strat2.name: 4
        }
    PnL_dict = {
            test_strat1.name: 100,
            test_strat2.name: 202
    }
    result = test_game.sql_parser(thresholds, test_balloon, PnL_dict)
    assert (45, "red", 5, test_strat1.name, 3, 100) in result
    assert (45, "red", 5, test_strat2.name, 4, 202) in result
    

@pytest.mark.engine
def test_initialization():
    # Test if same seed generates the same set of balloons
    seed = 101
    game_1 = Game([test_strat1, test_strat2], seed, 1, 100)
    game_2 = Game([test_strat1, test_strat2], seed, 2, 100)

    balloon_list_1 = game_1.initialization()
    balloon_list_2 = game_2.initialization()
    assert balloon_list_1 == balloon_list_2

    # Test if different seeds generate different balloons
    game_3 = Game([test_strat1, test_strat2], 102, 3, 100)
    game_4 = Game([test_strat1, test_strat2], 103, 4, 100)
    balloon_list_3 = game_3.initialization()
    balloon_list_4 = game_4.initialization()
    assert len(balloon_list_3) == len(balloon_list_4)
    booleans = [balloon_list_3[i] == balloon_list_4[i] for i in range(len(balloon_list_3))]
    assert all(booleans) == False

    # Test if balloon id are correct 
    # Test if probabilities are correct
    for i in range(len(balloon_list_1)):
        assert balloon_list_1[i].id == i
        assert balloon_list_1[i].prob == COLOR_MAP[balloon_list_1[i].color]
        assert balloon_list_1[i].pop_value >= 0

    # Test length of balloon list
    assert len(balloon_list_1) == 100


@pytest.mark.engine
def test_resolve_round():
    # Test if the order and type of the returns are correct
    threshold_1 = 6
    threshold_2 = 7
    thresholds = {
            test_strat1.name: threshold_1, 
            test_strat2.name: threshold_2
        }
    result = test_game.resolve_round(thresholds, test_balloon)
    assert isinstance(result[0], dict) and isinstance(result[1], list)
    for value in result[0].values():
        assert isinstance(value, Observation)
    for value in result[1]:
        assert isinstance(value, tuple)
        assert len(value) == 6
    


# TESTS FOR STRATEGIES

@pytest.mark.strategies
def test_action():
    pass

@pytest.mark.strategies
def test_update_beliefs():
    pass