

from strategies import Strategy

class config:
    def __init__(self, seed: int,  num_balloons: int, color_map: dict[str, float], strategies: list[Strategy]):
        self.seed = seed
        self.num_balloons = num_balloons
        self.color_map = color_map
        self.strategies = strategies
        