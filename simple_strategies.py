from Classes import Balloon
import pandas as pd
# Simple strategies for the balloon game
NUM_BALLOONS = 100

def constant_pump(balloon, memory):
    pars = memory[1]
    k = pars[0]
    if balloon.value < k:
        return "p"
    else:
        return "c"

class explore_then_exploit:
    def __init__(self, ratio: int, post_explore_updates: bool, memory: pd.DataFrame, num_balloons: int) -> None:
        self.post_explore_updates = post_explore_updates
        self.memory = memory
        self.ratio = ratio
        self.num_balloons = num_balloons

    def new_balloon_handling(self, balloon: Balloon):
        new_row = pd.DataFrame({"color": [balloon.color], "pumps": [0]})
        self.memory = pd.concat([self.memory, new_row], ignore_index=True)

    def old_balloon_handling(self, balloon: Balloon):
        self.memory.loc[self.memory[-1]] = {"color": balloon.color, "pumps": balloon.value}
    
    def unseen_color_handling(self, balloon: Balloon) -> str:
        # essentially assume a popping probability = 1/2
        if balloon.value < 1:
            return "p"
        else:
            return "c"
    def num_pumps(self, color: str) -> int:
        memory_grouped = self.memory.groupby("color").agg(avg_pump = ("pumps", "mean"))
        return memory_grouped.loc[color, "avg_pump"]
    
    def main(self, balloon: Balloon) -> str:
        if len(self.memory) < self.num_balloons * self.ratio:
            # We are in Exploration Phase
            if balloon.value < 1:
                # New balloon
                self.new_balloon_handling(balloon)
            else:
                # Existing balloon
                self.old_balloon_handling(balloon)
            return "p" 
        else:
            # Exploitation phase
            if balloon.color not in self.memory.index:
                self.unseen_color_handling(balloon)
            else:
                
                if balloon.value < self.num_pumps(balloon.color):
                    return "p"
                else:
                    return "c"
            






def explore_then_exploit(balloon, memory):
    memory_df = memory[0]
    pars = memory[1]
    ratio = pars[0]
    
    if len(memory_df) < NUM_BALLOONS * ratio:
        # We are still exploring
        if balloon.value < 1:
            # new balloon
            new_row = pd.DataFrame({"color": [balloon.color], "pumps": [0]})
            memory_df = pd.concat([memory_df, new_row], ignore_index=True)
        else:
            # existing balloon
            memory_df.loc[memory_df.index[-1]] = {"color": balloon.color, "pumps": balloon.value}
        # phase 1: explore phase: pump until we have enough data
        return "p"
    else:
        # phase 2: exploit phase: use the data to make a decision
        df_grouped = memory_df.groupby("color").agg(avg_pump=("pumps", "mean"))
        if balloon.color not in df_grouped.index:
            # If we don't have data just pump once
            if balloon.value < 1:
                return "p"
            else:
                return "c"
        if balloon.value < df_grouped.loc[balloon.color, "avg_pump"]:
            return "p"
        else:
            return "c"
        




    

    
