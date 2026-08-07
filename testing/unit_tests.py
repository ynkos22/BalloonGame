import sys
import os
import pytest

sys.path.inser(0,  os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules"))


# TESTS FOR ENGINE

@pytest.mark.engine
def test_obs_parser():
    pass

@pytest.mark.engine
def test_sql_parser():
    pass

@pytest.mark.engine
def test_calc_payout():
    pass

@pytest.mark.engine
def test_update_PnL():
    pass

@pytest.mark.engine
def test_initialization():
    pass

@pytest.mark.engine
def test_resolve_round():
    pass

@pytest.mark.engine
def test_balloon_loop():
    pass


# TESTS FOR STRATEGIES

@pytest.mark.strategies
def test_action():
    pass

@pytest.mark.strategies
def test_update_beliefs():
    pass