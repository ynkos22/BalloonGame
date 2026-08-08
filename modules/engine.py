
from strategies import Strategy
from sql_handling import SQL_handling
from core import Balloon, Observation
import numpy as np
import sqlite3
from config import DATABASE_PATH, COLOR_MAP


class Game:
    def __init__(self, strategies: list[Strategy], seed: int, game_id: int, num_balloons: int):
        self.strategies = strategies
        self.seed = seed
        self.game_id = game_id
        self.num_balloons = num_balloons
        self.balloon_rng, self.tiebreak_rng = np.random.default_rng(seed).spawn(2)

    # Returns a dictionary with player names and their respective payouts
    # This function is a bit long just covering all the cases of the rules of payout
    def calc_payout(self, thresholds: dict, balloon: Balloon) -> dict:
        pop_val = balloon.pop_value
        if len(thresholds) == 1:
            # Single-player
            strategy_name = list(thresholds.keys())[0]
            if thresholds[strategy_name] < pop_val and thresholds[strategy_name] >= 0:
                payout = {strategy_name: thresholds[strategy_name]}
            else:
                payout = {strategy_name: 0}
            return payout

        elif len(thresholds) == 2:
            # Multiplayer
            strategy_name_1, strategy_name_2 = thresholds.keys()
            threshold_1, threshold_2 = thresholds[strategy_name_1], thresholds[strategy_name_2]

            if threshold_1 >= pop_val:
                if threshold_2 >= pop_val: # both popped
                    payout = {strategy_name_1: 0, 
                              strategy_name_2: 0}
                else: # 1 popped, 2 didn't
                    payout = {strategy_name_1: 0, 
                            strategy_name_2: threshold_2}
            else: # 1 didn't pop
                if threshold_2 >= pop_val: # 1 didn't pop 2 did
                    payout = {strategy_name_1: threshold_1, 
                                strategy_name_2: 0}
                else: # neither popped
                    if threshold_1 == threshold_2:
                        if self.tiebreak_rng.random() < 0.5:
                            payout = {strategy_name_1: threshold_1 + threshold_2, strategy_name_2: 0}
                        else:
                            payout = {strategy_name_1: 0, strategy_name_2: threshold_1 + threshold_2}
                    else:
                        payout = {strategy_name_1: (threshold_1 + threshold_2)*int(threshold_1>threshold_2), 
                                strategy_name_2: (threshold_1 + threshold_2)*int(threshold_1<threshold_2)}
            return payout
        else:
            return {}
    

    # Updates players' PnL according payouts
    # Returns updated PnL in dictionary (keys are strategy names)
    def update_PnL(self, strategies: list[Strategy], payout:dict) -> dict[str, int]:
        PnL_dict = {}
        for strategy in strategies:
            if strategy.name in payout:
                strategy.PnL += payout[strategy.name]
                PnL_dict[strategy.name] = strategy.PnL
            else:
                PnL_dict[strategy.name] = strategy.PnL

        return PnL_dict
    
    # Returns an dictionary with names and Observation objects
    # used in resolve_round before returning Observation object
    def obs_parser(self, thresholds: dict, payout: dict, color: str) -> dict[str, Observation]:
        obs_dict = {}
        for strat in self.strategies:
            obs_dict[strat.name] = Observation(payout, thresholds[strat.name], color)
        return obs_dict


    # Returns a list of tuples ready to be inserted into SQL table
    # entries: (balloon_id, balloon_color, pop_time, strategy_name, threshold, end_PnL)
    def sql_parser(self, thresholds: dict, balloon: Balloon, PnL_dict: dict[str, int]) -> list[tuple]:
        return_list = []
        balloon_id = balloon.id
        balloon_color = balloon.color
        pop_time = balloon.pop_value
        for strategy in self.strategies:
            strategy_name = strategy.name
            threshold = thresholds[strategy_name]
            end_PnL = PnL_dict[strategy_name]
            return_list.append((balloon_id, balloon_color, pop_time, strategy_name, threshold, end_PnL))
        return return_list
      

    # Returns a list of balloons at the start of each round 
    # Same seed should return same balloons (colors, pop values, and probability)
    def initialization(self) -> list[Balloon]:
        balloon_list = []
        rng = self.balloon_rng
        colors = list(COLOR_MAP.keys())
        for i in range(self.num_balloons):
            color = rng.choice(colors)
            probability = COLOR_MAP[color]
            pop_value = rng.geometric(probability)
            balloon_list.append(Balloon(color, pop_value, probability, i))
            
        return balloon_list

    # Returns a tuple with the following content
    # index 0: dict: player_name -> observation object
    # index 1: dict: player name -> tuple for insertion into sql table
    def resolve_round(self, thresholds: dict, balloon: Balloon) -> tuple[dict[str, Observation], list[tuple]]:
        payout = self.calc_payout(thresholds, balloon)
        PnL_dict = self.update_PnL(self.strategies, payout)

        sql_list = self.sql_parser(thresholds, balloon, PnL_dict)
        obs_dict = self.obs_parser(thresholds, payout, balloon.color)

        return (obs_dict, sql_list)

    # Iterates through all balloons 
    # Each player makes a decision
    # Round is resolved 
    # Beliefs are updated
    # SQL tables are updated
    def balloon_loop(self, strategies: list[Strategy], balloons: list[Balloon]) -> None:
        conn = sqlite3.Connection(DATABASE_PATH)
        SQL_handler = SQL_handling(conn, self.game_id)

        for balloon in balloons:
            thresholds = {}
            for strategy in strategies:
                # insert strategy decisions into thresholds
                thresholds[strategy.name] = strategy.action(balloon)
            obs_dict, sql_list = self.resolve_round(thresholds, balloon)

            # Update strategy beliefs
            for strategy in strategies:
                strategy.update_beliefs(obs_dict[strategy.name])

            # record into SQL table
            SQL_handler.sql_insert(sql_list) #NOTE: not ONE tuple but a list of tuples

        conn.commit()
        conn.close()

    # Main loop that runs once per game
    def main(self):
        balloon_list = self.initialization()
        self.balloon_loop(self.strategies, balloon_list)
        
        


