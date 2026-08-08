


class Balloon:
    def __init__(self, color: str, pop_value: int, prob: float, id: int):
        self.color = color
        self.pop_value = pop_value
        self.prob = prob
        self.id = id

    def __eq__(self, other):
        return all([self.color == other.color, self.pop_value == other.pop_value, self.id == other.id, self.prob == other.prob, isinstance(other, Balloon)])
        

class Observation:
    def __init__(self, payout: dict, own_threshold: int, balloon_color: str, pop_time=999):
        self.payout = payout.copy()
        self.own_threshold = own_threshold
        self.balloon_color = balloon_color
        self.pop_time = pop_time # if it didn't pop default == 999
        