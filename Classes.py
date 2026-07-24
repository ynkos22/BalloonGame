
from collections.abc import Callable
import random
from typing import List
import pandas as pd
import sqlite3



class Balloon:
    def __init__(self, color: str, value: int, popped: bool, probability=None) -> None:
        self.color = color
        self.value = value
        self.popped = popped
        self.probability = probability
    
    def pop(self) -> None:
        self.popped = True
        self.value = 0
    
    def pop_prob(self) -> float:
        if self.probability is not None:
            return self.probability
        color = self.color
        color_prob_map = {
            "yellow": 0.1,
            "red": 0.3, 
            "blue": 0.5,
            "brown":0.8
        }
        return color_prob_map[color]

    def inflate(self) -> None:
        random_val = random.random()
        prob = self.pop_prob()
        if random_val > prob:
            self.value += 1
            
        else:
            self.pop()

# Parent class of all other strategies
class Strategy:
    def __init__(self, name: str, unrPnL: int, PnL: int, db_path: str):
        self.name = name
        self.unrPnL = unrPnL
        self.PnL = PnL
        self.conn = sqlite3.connect(db_path)

    # Default action that all strategies will use if not specified otherwise
    def action(self, balloon: Balloon) -> str:
        if balloon.value < 1:
            return "p"
        else:
            return "c"   
        
    # Note: this is the method that is called during game loop FOR ALL strategies
    def main(self, balloon) -> str:
        move = self.action(balloon)
        if move == "p":
            Balloon.inflate(balloon)
            if balloon.popped:
                self.unrPnL = 0
            else:
                self.unrPnL += 1
        if move == "c":
            self.PnL += self.unrPnL
            self.unrPnL = 0
        return move

class Game:
    
    def __init__(self, players: list[Strategy], num_balloons: int, id: int, db_path: str) -> None:
        self.players = players
        self.num_balloons = num_balloons
        self.id = id
        self.conn = sqlite3.connect(db_path)
        cur = self.conn.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS game_{self.id}(turn INTEGER, 
                                            balloon_number INTEGER, 
                                            balloon_color TEXT, 
                                            balloon_value INTEGER, 
                                            strategy_name TEXT, 
                                            player_action TEXT, 
                                            popped INTEGER, 
                                            player_unrPnL INTEGER, 
                                            player_PnL INTEGER)""")
        self.conn.commit()

    # This method runs the game
    def start(self) -> None:
        # generate balloons:
        balloons = [Balloon(color=random.choice(["yellow", "red", "blue"]), value=0, popped=False) for _ in range(self.num_balloons)]
        # start game loop:
        for player in self.players:
            self.per_player_game_loop(balloons, player)
                   
    @staticmethod
    def reset_balloons(balloons: List[Balloon]) -> None:
        for balloon in balloons:
            balloon.value = 0
            balloon.popped = False
        return balloons

    # Returns the log of each turn and what player/strategy did
    def per_turn_game_loop(self, balloon: Balloon, balloon_number: int, turn: int, player: Strategy) -> dict:
        # We first report the current state of the game before the player takes an action
        log = {
            "balloon_value": balloon.value, 
            "balloon_color": balloon.color,
            "balloon_number": balloon_number + 1,
            "turn": turn + 1,
            "player_unrPnL": player.unrPnL,
            "player_PnL": player.PnL,
            "player_name": player.name
        }
        action = player.main(balloon) # Player action
        # Update the log with the action taken and whether the balloon popped
        log["popped"] = balloon.popped
        log["player_action"] = action
        return log, action
    
    def per_balloon_game_loop(self, balloons: List[Balloon], balloon_number: int, turn: int, player: Strategy) -> dict:
        current_balloon = balloons[balloon_number]
        cash = False
        current_turn = turn
        # Loop until the balloon pops or the player cashes out
        while not current_balloon.popped and not cash:
            log, action = self.per_turn_game_loop(current_balloon, balloon_number, current_turn, player)
            cur = self.conn.cursor()
            cur.execute(f"INSERT INTO game_{self.id} (?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.id, 
                                                                           log["turn"]+1, 
                                                                           log["balloon_number"]+1, 
                                                                           log["balloon_value"], 
                                                                           player.name, 
                                                                           action, 
                                                                           current_balloon.popped, 
                                                                           log["player_unrPnL"], 
                                                                           log["player_PnL"]))
            self.conn.commit()
            current_turn += 1
            if action == "c":
                cash = True
        return current_turn

    def per_player_game_loop(self, balloons: List[Balloon], player: Strategy) -> pd.DataFrame:
        # reset balloons before each player starts
        balloons = self.reset_balloons(balloons)
        current_turn = 0
        current_balloon_number = 0
        while current_balloon_number < self.num_balloons:
            current_turn = self.per_balloon_game_loop(balloons, current_balloon_number, current_turn, player)
            current_balloon_number += 1
        
    # Converts relavant part of database into csv doc
    # and saves it into game_logs
    # file name: "game_{game_id}_log"
    @staticmethod
    def print_summary(game_id: int) -> None:
        conn = sqlite3.Connection("game_logs.db")

        game_log = pd.read_sql_query(f"SELECT * FROM game_{game_id}", conn)
        game_log.to_csv(f"game_logs/game_{game_id}_log", index = False)
        





