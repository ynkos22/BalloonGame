from Classes import Balloon, Strategy
import pandas as pd
import numpy as np


# Simple strategies for the balloon game

# CONSTANT PUMP STRATEGY: Keep pumping the balloon until it reaches a value k
class constant_pump(Strategy):
    def __init__(self, k: int):
        super().__init__(name = "Constant_pump")
        self.k = k

    def action(self, balloon: Balloon) -> str:
        if balloon.value < self.k:
            return "p"
        else:
            return "c"


class explore_then_exploit(Strategy):
    def __init__(self, ratio: int, num_balloons: int, game_id: int) -> None:
        super().__init__(name="Explore then Exploit")
        self.ratio = ratio
        self.num_balloons = num_balloons
        self.game_id = game_id

    def unseen_color_handling(self, balloon: Balloon) -> str:
        # essentially assume a popping probability = 1/2
        return super().action(balloon)
    
    # Returns average lifespan of balloons of certain color
    def num_pumps(self, color: str) -> float:
        
        cur = self.conn.cursor()
        cur.execute(f"""SELECT balloon_color AS color, AVG(end_value) as average_lifespan 
                    FROM (SELECT balloon_color, balloon_number, MAX(balloon_value-1) AS end_value FROM game_{self.game_id} WHERE balloon_color = ? GROUP BY balloon_number)""", (color,))
        row = cur.fetchone()
        return row[1]
        
    # Takes in a balloon and returns aproprate move ("p" or "c")
    # Uses average lifespan of the color of balloon 
    # This overrides parent class default action method
    def action(self, balloon: Balloon) -> str:
        
        # Checks how many balloons we have seen
        cur = self.conn.cursor()
        cur.execute(f"SELECT COUNT(DISTINCT balloon_number) from game_{self.game_id}")
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
    

    
            
        




    

    
