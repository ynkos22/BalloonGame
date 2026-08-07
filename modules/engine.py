
from strategies import Strategy
from sql_handling import SQL_handling

class Balloon:
    def __init__(self, color: str, pop_value: int, prob: float):
        self.color = color
        self.pop_value = pop_value
        self.prob = float

class Observation:
    def __init__(self, payout: dict, own_threshold: int, balloon_color: str):
        self.payout = payout
        self.own_threshold = own_threshold
        self.balloon_color = balloon_color
        


class Game:
    def __init__(self, strategies: list[Strategy], seed: int, game_id: int):
        self.strategies = strategies
        self.seed = seed
        self.game_id = game_id

    # Returns a tuple with the following content
    # index 0: dict: player_name -> observation objects
    # index 1: tuple for insertion into sql table
    def resolve_round(self, thresholds: dict, balloon: Balloon) -> tuple[Observation, Observation, tuple]:
        payout = self.calc_payout(thresholds, balloon)
        self.update_PnL(*self.strategies, payout)

        sql_tuple = self.sql_parser(thresholds, balloon)
        obs_dict = self.obs_parser(thresholds, payout)

        return (obs_dict, sql_tuple)

    # Returns a tuple ready to be inserted into SQL table
    def sql_parser(self, thresholds: dict, balloon: Balloon) -> tuple:
        pass

    # Returns an Observation object
    # used in resolve_round before returning Observation object
    def obs_parser(self, thresholds: dict, payout: dict) -> dict[str, Observation]:
        pass

    # Returns a dictionary with player names and their respective payouts
    def calc_payout(self, thresholds: dict, balloon: Balloon) -> dict:
        pass

    # Updates players' PnL according payouts
    def update_PnL(self, strategy_1: Strategy, strategy_2: Strategy, payout:dict) -> None:
        pass

    # Returns a list of balloons at the start of each round 
    # Same seed should return same balloons (colors, pop values, and probability)
    def initialization(self, seed: int) -> list[Balloon]:
        pass

    # Iterates through all balloons 
    # Each player makes a decision
    # Round is resolved 
    # Beliefs are updated
    # SQL tables are updated
    def balloon_loop(self, strategies: list[Strategy], balloons: list[Balloon]) -> None:

        for balloon in balloons:
            thresholds = [strategy.action(balloon) for strategy in strategies]
            obs_dict, sql_tup = self.resolve_round(thresholds, balloon)

            # Update strategy beliefs
            for strategy in strategies:
                strategy.update_beliefs(obs_dict[strategy.name])

            # record into SQL table
            SQL_handling.sql_insert(sql_tup)

    # Main loop that runs once per game
    def main(self):
        balloon_list = self.initialization(self.seed)
        self.balloon_loop(self.strategies, balloon_list)
        
        


