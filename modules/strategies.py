from core import Balloon, Observation
from config import COLOR_MAP
import numpy as np



class Strategy:
    def __init__(self, name: str):
        self.name = name
        self.PnL = 0
        
        self.belief_state = {} # each color and the corresponding threshold
        colors = list(COLOR_MAP.keys())
        for color in colors:
            self.belief_state[color] = 1
        
        
    # Returns the pump threshold (at which value to cash) for a balloon
    def action(self, balloon: Balloon) -> int:
        return 1 # default pump

    # updates strategies' beliefs
    def update_beliefs(self, obs: Observation) -> None:
        pass

    # Infers how many successful and unsuccesful pumps from own_threshold and pop_val
    # The opponent's payout is deliberately ignored: it only reveals how deep the balloon
    # went when the opponent SURVIVED, so using it would censor at an outcome-dependent
    # depth and bias the pop-probability estimate downwards.
    # returns np.array([num_suc, num_fail])
    def payout_infer(self, own_threshold: int, pop_val: int) -> np.array:
        result_list = [0, 0]
        if pop_val == 999:
            result_list[0] += own_threshold
        else:
            result_list[0] += max(pop_val-1, 0)
            result_list[1] += 1
        return np.array(result_list)

        

class constant_pump(Strategy):
    def __init__(self, pump_times: int):
        super().__init__(name = f"constant_pump_{pump_times}")
        self.pump_times = pump_times

    def action(self, balloon: Balloon) -> int:
        return self.pump_times


class explore_exploit(Strategy):
    def __init__(self, ratio, num_balloons):
        super().__init__(name=f"explore_exploit_{ratio}")
        self.ratio = ratio
        self.num_balloons = num_balloons
        self.memory = {}
        colors = list(COLOR_MAP.keys())
        for color in colors:
            self.memory[color] = np.array([1, 1])

    def action(self, balloon: Balloon) -> int:
        if balloon.id <= self.ratio * self.num_balloons:
            # Exploration phase
            return 1000
        else:
            return self.belief_state[balloon.color]

    def update_beliefs(self, obs: Observation):

        succ_fail_vector = self.payout_infer(obs.own_threshold, obs.pop_time)

        # Update self.memory
        self.memory[obs.balloon_color] += succ_fail_vector
        
        # Update self.belief_state
        p = self.memory[obs.balloon_color][1]/(self.memory[obs.balloon_color][0] + self.memory[obs.balloon_color][1])
        self.belief_state[obs.balloon_color] = max(1, int(np.ceil((1-p)/p)))

class thompson_sampling(Strategy):
    def __init__(self):
        super().__init__(name = "thompson_sampling")
        self.memory = {}
        colors = list(COLOR_MAP.keys())
        for color in colors:
            self.memory[color] = np.array([1, 1])

    def action(self, balloon: Balloon) -> int:
        return self.belief_state[balloon.color]

    def update_beliefs(self, obs: Observation):
        succ_fail_vector = self.payout_infer(obs.own_threshold, obs.pop_time)
        
        # Update self.memory
        self.memory[obs.balloon_color] += succ_fail_vector

        p = self.thompson_sampler(*self.posterior(obs.balloon_color))
        self.belief_state[obs.balloon_color] = self.decision_rule(p)

    def posterior(self, color):
        return self.memory[color]

    # Given Beta posterior parameters, this function samples a probability p from this distribution
    def thompson_sampler(self, a: int, b: int) -> float:
        sample = np.random.beta(b, a)
        return sample

    def decision_rule(self, p: float):
        return max(1, int(np.ceil((1-p)/p)))


class oracle(Strategy):
    def __init__(self):
        super().__init__(name = "oracle")

    def action(self, balloon: Balloon):
        p = COLOR_MAP[balloon.color]
        return max(1, int(np.ceil((1-p)/p)))
    


    
    

        

