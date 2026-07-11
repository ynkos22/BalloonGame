
from collections.abc import Callable
import random
from typing import List
import pandas as pd
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


class Player:
    def __init__(self, strategy: Callable[[Balloon, list], str], id: int, unrPnL: int, PnL: int, memory: list) -> None:
        self.strategy = strategy
        self.id = id
        self.unrPnL = unrPnL
        self.PnL = PnL
        self.memory = memory

    def action(self, balloon) -> str:
        move = self.strategy(balloon, self.memory)
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
    def __init__(self, players: list[Player], num_balloons: int, id: int) -> None:
        self.players = players
        self.num_balloons = num_balloons
        self.id = id

    def start(self) -> None:
        # generate balloons:
        balloons = [Balloon(color=random.choice(["yellow", "red", "blue"]), value=0, popped=False) for _ in range(self.num_balloons)]
        # start game loop:
        for player in self.players:
            game_log = self.per_player_game_loop(balloons, player)
        game_log.to_csv(f"game_logs/game_{self.id}_player_{player.id}_log.csv", index = False)
            
    @staticmethod
    def reset_balloons(balloons: List[Balloon]) -> None:
        for balloon in balloons:
            balloon.value = 0
            balloon.popped = False
        return balloons

    def per_turn_game_loop(self, balloon: Balloon, balloon_number: int, turn: int, player: Player) -> dict:
        # We first report the current state of the game before the player takes an action
        log = {
            "balloon_value": balloon.value, 
            "balloon_color": balloon.color,
            "balloon_number": balloon_number + 1,
            "turn": turn + 1,
            "player_unrPnL": player.unrPnL,
            "player_PnL": player.PnL,
            "player_id": player.id
        }
        action = player.action(balloon) # Player action
        # Update the log with the action taken and whether the balloon popped
        log["popped"] = balloon.popped
        log["player_action"] = action
        return log, action
    
    def per_balloon_game_loop(self, balloons: List[Balloon], balloon_number: int, turn: int, player: Player, game_log: pd.DataFrame) -> dict:
        current_balloon = balloons[balloon_number]
        cash = False
        current_turn = turn
        # Loop until the balloon pops or the player cashes out
        while not current_balloon.popped and not cash:
            log, action = self.per_turn_game_loop(current_balloon, balloon_number, current_turn, player)
            game_log = pd.concat([game_log, pd.DataFrame([log])], ignore_index=True)
            current_turn += 1
            if action == "c":
                cash = True
        return game_log, current_turn

    def per_player_game_loop(self, balloons: List[Balloon], player: Player) -> pd.DataFrame:
        #reset balloons before each player starts
        balloons = self.reset_balloons(balloons)
        game_log = pd.DataFrame(columns=["turn", "balloon_number", "balloon_color", "balloon_value", "player_id", "player_action", "popped", "player_unrPnL", "player_PnL"])
        current_turn = 0
        current_balloon_number = 0
        while current_balloon_number < self.num_balloons:
            results = self.per_balloon_game_loop(balloons, current_balloon_number, current_turn, player, game_log)
            current_turn = results[1]
            current_balloon_number += 1
            
        return game_log
        
    @staticmethod
    def print_summary(game_log: pd.DataFrame) -> None:
        # outputs a more readable summary of the game log as a csv file
        summary = game_log.groupby("balloon_number").agg(
            color = ("balloon_color", "first"),
            value = ("balloon_value", "max"),
            num_pumps = ("player_action", lambda x: (x == "p").sum()),
            popped = ("popped", "max"),
            turns = ("turn", "count"),
            player_unrPnL = ("player_unrPnL", "last"),
            player_PnL = ("player_PnL", "last")
        )
        
        summary.to_csv(f"games/game_{self.id}_summary.csv")






