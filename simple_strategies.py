from Classes import Balloon, Strategy
import pandas as pd
import numpy as np
import sqlite3
from config import DATABASE_PATH

# Simple strategies for the balloon game

# CONSTANT PUMP STRATEGY: Keep pumping the balloon until it reaches a value k
class constant_pump(Strategy):
    def __init__(self, k: int):
        super().__init__(name = f"Constant_pump_{k}")
        self.k = k

    def action(self, balloon: Balloon) -> str:
        if balloon.value < self.k:
            return "p"
        else:
            return "c"


class explore_then_exploit(Strategy):
    def __init__(self, ratio: int, num_balloons: int, game_id: int, player_id: int) -> None:
        super().__init__(name=f"explore_exploit_{player_id}")
        self.ratio = ratio
        self.num_balloons = num_balloons
        self.game_id = game_id
        self.conn = sqlite3.Connection(DATABASE_PATH)

    def unseen_color_handling(self, balloon: Balloon) -> str:
        # essentially assume a popping probability = 1/2
        return super().action(balloon)
    
    # Returns average lifespan of balloons of certain color
    def num_pumps(self, color: str) -> float:
        
        cur = self.conn.cursor()
        cur.execute(f"""SELECT * FROM (
        SELECT balloon_color, AVG(end_value) FROM (
        SELECT balloon_number, balloon_color, MAX(balloon_value) as end_value FROM (
        SELECT * FROM (SELECT * from game_{self.game_id} WHERE strategy_name = ?) WHERE balloon_number <= ?) GROUP BY balloon_number) GROUP BY balloon_color) WHERE balloon_color = ?""", (self.name, self.num_balloons, color))
        row = cur.fetchone()
        return row[1]
        
    # Takes in a balloon and returns aproprate move ("p" or "c")
    # Uses average lifespan of the color of balloon 
    # This overrides parent class default action method
    def action(self, balloon: Balloon) -> str:
        
        # Checks how many balloons we have seen
        cur = self.conn.cursor()
        cur.execute(f"SELECT COUNT(DISTINCT balloon_number) from game_{self.game_id} WHERE strategy_name = ?", (self.name,))
        db_size = cur.fetchone()[0]
        
        if db_size < self.num_balloons * self.ratio:
            # We are in Exploration Phase
            return "p" 
        else:
            # Exploitation phase
            cur.execute(f"SELECT DISTINCT balloon_color from game_{self.game_id}")
            seen_colors_tuples = cur.fetchall()
            seen_colors = [tuple[0] for tuple in seen_colors_tuples]
            if balloon.color not in seen_colors:
                # If we haven't seen color assume 1/2 probability
                return self.unseen_color_handling(balloon)
            else: 
                average_lifespan = self.num_pumps(balloon.color) # Note: this is a float
                if balloon.value < np.floor(average_lifespan):
                    return "p"
                else:
                    return "c"
    

        
class thompson_sampling(Strategy):
    def __init__(self, game_id: int):
        super().__init__(name="thompson_sampling")
        self.game_id = game_id

    # Given a color, this function outputs the beta posterior parameters (a, b)
    # a: number of unsuccessful pumps + 1
    # b: number of successful pumps + 1
    def posterior(self, color: str) -> tuple[int, int]:
        conn = sqlite3.Connection(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute(f"""SELECT COALESCE(SUM(popped), 0) + 1 as a, COALESCE(SUM(1-popped), 0) + 1 as b FROM (
                        SELECT * FROM (
                        SELECT * FROM (SELECT balloon_color, player_action, popped from game_{self.game_id} WHERE strategy_name = "thompson_sampling") 
                        WHERE player_action = "p") 
                        WHERE balloon_color = ?)""", (color,))
        row = cur.fetchone()
        conn.close()
        a = row[0]
        b = row[1]
        return (a, b)

    # Given Beta posterior parameters, this function samples a probability p from this distribution
    def thompson_sampler(self, a: int, b: int) -> float:
        sample = np.random.beta(a, b)
        return sample

    # Given balloon is at value v, and our estimated probability is p
    # this function returns "p" for pump and "c" for cash
    def decision_rule(self, v: int, p: float) -> str:
        if v < (1-p)/p:
            return "p"
        else:
            return "c"

    def action(self, balloon: Balloon) -> str:

        color = balloon.color
        value = balloon.value
        posterior = self.posterior(color)
        beta_a = posterior[0]
        beta_b = posterior[1]

        p_estimate = self.thompson_sampler(beta_a, beta_b)

        return self.decision_rule(value, p_estimate)




    

    
