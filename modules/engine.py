
from strategies import Strategy
from sql_handling import SQL_handling
from core import Balloon, Observation





class Game:
    def __init__(self, strategies: list[Strategy], seed: int, game_id: int, num_balloons: int):
        self.strategies = strategies
        self.seed = seed
        self.game_id = game_id
        self.num_balloons

    # Returns a dictionary with player names and their respective payouts
    def calc_payout(self, thresholds: dict, balloon: Balloon) -> dict:
        pass

    # Updates players' PnL according payouts
    # Returns updated PnL in dictionary (keys are strategy names)
    def update_PnL(self, strategies: list[Strategy], payout:dict) -> dict[str, int]:
        pass

    # Returns an dictionary with names and Observation objects
    # used in resolve_round before returning Observation object
    def obs_parser(self, thresholds: dict, payout: dict, color: str) -> dict[str, Observation]:
        pass


    # Returns a dictionary with names with tuples ready to be inserted into SQL table
    # entries: (balloon_id, balloon_color, pop_time, strategy_name, threshold, end_PnL)
    def sql_parser(self, thresholds: dict, balloon: Balloon, PnL_dict: dict[str, int]) -> dict[str, tuple]:
        pass

    # Returns a list of balloons at the start of each round 
    # Same seed should return same balloons (colors, pop values, and probability)
    def initialization(self) -> list[Balloon]:
        pass

    # Returns a tuple with the following content
    # index 0: dict: player_name -> observation object
    # index 1: dict: player name -> tuple for insertion into sql table
    def resolve_round(self, thresholds: dict, balloon: Balloon) -> tuple[dict[str, Observation], dict[str, tuple]]:
        payout = self.calc_payout(thresholds, balloon)
        PnL_dict = self.update_PnL(self.strategies, payout)

        sql_dict = self.sql_parser(thresholds, balloon, PnL_dict)
        obs_dict = self.obs_parser(thresholds, payout, balloon.color)

        return (obs_dict, sql_dict)

    # Iterates through all balloons 
    # Each player makes a decision
    # Round is resolved 
    # Beliefs are updated
    # SQL tables are updated
    def balloon_loop(self, strategies: list[Strategy], balloons: list[Balloon]) -> None:

        for balloon in balloons:
            thresholds = {}
            for strategy in strategies:
                # insert strategy decisions into thresholds
                thresholds[strategy.name] = strategy.action(balloon)
            obs_dict, sql_dict = self.resolve_round(thresholds, balloon)

            # Update strategy beliefs
            for strategy in strategies:
                strategy.update_beliefs(obs_dict[strategy.name])

            # record into SQL table
            SQL_handling.sql_insert(sql_dict) #NOTE: not ONE tuple but a dict

    # Main loop that runs once per game
    def main(self):
        balloon_list = self.initialization()
        self.balloon_loop(self.strategies, balloon_list)
        
        


