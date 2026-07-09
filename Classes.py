
from collections.abc import Callable
import random
import pandas as pd
class Balloon:
    def __init__(self, color: str, value: int, popped: bool) -> None:
        self.color = color
        self.value = value
        self.popped = popped
    
    def pop(self) -> None:
        self.popped = True
    
    def pop_prob(self) -> float:
        color = self.color
        color_prob_map = {
            "yellow": 0.1,
            "red": 0.1, 
            "blue": 0.7
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
    def __init__(self, strategy: Callable[[Balloon], str], id: int, unrPnL: int, PnL: int) -> None:
        self.strategy = strategy
        self.id = id
        self.unrPnL = unrPnL
        self.PnL = PnL

    def action(self, balloon) -> str:
        move = self.strategy(balloon)
        if move == "p":
            Balloon.inflate(balloon)
            if balloon.popped:
                self.unrPnL -= balloon.value
            else:
                self.unrPnL += 1
        if move == "c":
            self.PnL += self.unrPnL
            self.unrPnL = 0
        return move
        

class Game:
    def __init__(self, players: list[Player], num_balloons: int) -> None:
        self.players = players
        self.num_balloons = num_balloons

    def start(self) -> pd.DataFrame:
        
        # generate balloons:
        balloons = [Balloon(color=random.choice(["yellow", "red", "blue"]), value=0, popped=False) for _ in range(self.num_balloons)]
        # start game loop:
        game_log = pd.DataFrame(columns=["turn", "balloon_number", "balloon_color", "balloon_value", "player_id", "player_action", "popped", "player_unrPnL", "player_PnL"])
        current_turn = 0
        current_balloon_number = 0
        player = self.players[0]
        while current_balloon_number < self.num_balloons:
            current_balloon = balloons[current_balloon_number]
            cash = False
            while not current_balloon.popped and not cash:
                log = {}
                log["balloon_value"] = current_balloon.value
                log["balloon_color"] = current_balloon.color
                log["balloon_number"] = current_balloon_number + 1
                log["turn"] = current_turn + 1
                log["player_unrPnL"] = player.unrPnL
                log["player_PnL"] = player.PnL
                log["player_id"] = player.id
                action = player.action(current_balloon)
                if action == "c":
                    cash = True
                log["popped"] = current_balloon.popped
                log["player_action"] = action
                game_log = pd.concat([game_log, pd.DataFrame([log])], ignore_index=True)
                current_turn += 1
            current_balloon_number += 1
        return game_log

    def print_summary(self, game_log: pd.DataFrame) -> None:
        print("Game Summary:")
        print(f"Total Balloons: {self.num_balloons}")
        for player in self.players:
            player_log = game_log[game_log["player_id"] == player.id]
            print(f"Player {player.id}:")
            print(f"  Total PnL: {player.PnL}")
            print(f"  Total UnrPnL: {player.unrPnL}")
            print(f"  Total Actions: {len(player_log)}")
            print(f"  Total Pops: {len(player_log[player_log['popped'] == True])}")


