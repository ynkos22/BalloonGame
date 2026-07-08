
from collections.abc import Callable
import random

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
            "red": 0.3, 
            "blue": 0.7
        }
        return color_prob_map[color]

    def inflate(self):
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
        return self.strategy(balloon)

    


