
from collections.abc import Callable
import random
from typing import List
import pandas as pd
import sqlite3
from config import DATABASE_PATH, GAME_LOGS_CSV_FOLDER_PATH, COLOR_MAP


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
        color_prob_map = COLOR_MAP
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
    def __init__(self, name: str):
        self.name = name
        self.unrPnL = 0
        self.PnL = 0

    # Default action that all strategies will use if not specified otherwise
    def action(self, balloon: Balloon) -> str:
        if balloon.value < 1:
            return "p"
        else:
            return "c"   
        
    # NOTE: this is the method that is called during game loop FOR ALL strategies
    # returns strategy's action/move on a certain balloon
    # updates unrealized PnL and PnL apropriately
    # NOTE: cashed balloons are NOT reset, but popped balloons ARE
    def main(self, balloon) -> str:
        move = self.action(balloon)
        if move == "p":
            Balloon.inflate(balloon)
            self.unrPnL = balloon.value
        if move == "c":
            self.PnL += self.unrPnL
            self.unrPnL = 0
        return move



# Each game initiated with this class
# Initiation connects to SQL database 
# To run / start a game, use .start()
# To reset a game, use .clear_game(game_id)

class Game:

    def __init__(self, players: list[Strategy], num_balloons: int, id: int) -> None:
        self.players = players
        self.num_balloons = num_balloons
        self.id = id
        self.conn = sqlite3.connect(DATABASE_PATH)
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
            if hasattr(player, "conn"):
                player.conn.close()


    # Converts relavant part of database into csv doc
    # and saves it into game_logs
    # file name: "game_{game_id}_log"
    @staticmethod
    def print_summary(game_id: int) -> None:
        conn = sqlite3.Connection(DATABASE_PATH)

        game_log = pd.read_sql_query(f"SELECT * FROM game_{game_id}", conn)
        game_log.to_csv(GAME_LOGS_CSV_FOLDER_PATH + f"game_{game_id}_log", index = False)
        conn.close()

    # Clears the table in SQL database corresponding to a particular game
    @staticmethod
    def clear_game(game_id: int) -> None:
        conn = sqlite3.Connection(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute(f"DELETE FROM game_{game_id}")
        conn.commit()
        conn.close()

    @staticmethod
    def clear_db():
        conn = sqlite3.Connection(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("DROP DATABASE game_logs; CREATE DATABASE game_logs")

# Helper functions :

    # This method resets popped status and value of balloons
    # This is used in the before every player's turn
    # Returns list of balloons reset
    @staticmethod
    def reset_balloons(balloons: List[Balloon]) -> None:
        for balloon in balloons:
            balloon.value = 0
            balloon.popped = False
        return balloons


    # Highest level loop that runs for every player
    # Goes through all balloons in the list asking player for their action 
    # This runs until player has popped or cashed all balloons in the list
    # NOTE: turn and balloon_number are 0-indexed, but are logged as 1-indexed
    def per_player_game_loop(self, balloons: List[Balloon], player: Strategy) -> pd.DataFrame:
        # reset balloons before each player starts
        balloons = self.reset_balloons(balloons)

    
        current_turn = 0
        current_balloon_number = 0

        while current_balloon_number < self.num_balloons:
            current_turn = self.per_balloon_loop(balloons, current_balloon_number, current_turn, player)
            current_balloon_number += 1


    # This loop runs once per balloon (same balloon can survive multiple turns)
    # This function 
    # 1. returns the turn number after the balloon has been either cashed or popped (i.e the next turn number)
    # 2. records log in SQL database: turn, balloon_number, balloon_color, balloon_value, name of strat, action, popped?, unr_PnL, PnL

    def per_balloon_loop(self, balloons: List[Balloon], balloon_number: int, turn: int, player: Strategy) -> dict:

        # NOTE: balloon_number is 0-indexed
        # cashed == True if player cashed

        current_balloon = balloons[balloon_number]
        cashed = False
        current_turn = turn

        # Loop until the balloon pops or the player cashes out
        while not current_balloon.popped and not cashed:
            
            log = self.per_turn_game_loop(current_balloon, balloon_number, current_turn, player)
            action = log["player_action"]
            # Records in SQL DATABASE
            cur = self.conn.cursor()
            cur.execute(f"INSERT INTO game_{self.id} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (log["turn"], 
                                                                            log["balloon_number"], 
                                                                            log["balloon_color"],
                                                                            log["balloon_value"], 
                                                                            player.name, 
                                                                            action, 
                                                                            current_balloon.popped, 
                                                                            log["player_unrPnL"], 
                                                                            log["player_PnL"]))
            self.conn.commit()

            # Updates turn number
            current_turn += 1

            # Checks if player cashed
            if action == "c":
                cashed = True
        return current_turn

    # This runs at each turn (could be the same balloon for several turns)
    # Returns the log of each turn and what player/strategy did as a dict
    def per_turn_game_loop(self, balloon: Balloon, balloon_number: int, turn: int, player: Strategy) -> tuple[dict, str]:

        # We first report the current state of the game before the player takes an action
        log = {
            "balloon_value": balloon.value, 
            "balloon_color": balloon.color,
            "balloon_number": balloon_number + 1,
            "turn": turn + 1,
            "player_unrPnL": player.unrPnL,
            "player_PnL": player.PnL,
            "strategy_name": player.name
        }

        action = player.main(balloon) # Player action

        # Update the log with the action taken and whether the balloon popped
        log["popped"] = balloon.popped
        log["player_action"] = action
        return log
    
    


    



