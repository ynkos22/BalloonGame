from engine import Balloon, Observation


class Strategy:
    def __init__(self, name: str, PnL: int):
        self.name = name
        self.PnL = PnL
        self.belief_state = {} # each color and the corresponding threshold
        
    # Returns the pump threshold (at which value to cash) for a balloon
    def action(self, balloon: Balloon) -> int:
        pass

    # updates strategies' beliefs
    def update_beliefs(self, obs: Observation) -> None:
        pass