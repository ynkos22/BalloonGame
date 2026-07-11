from Classes import Balloon, Strategy
import pandas as pd
import numpy as np


# Simple strategies for the balloon game

def constant_pump(balloon, memory):
    pars = memory[1]
    k = pars[0]
    if balloon.value < k:
        return "p"
    else:
        return "c"

class explore_then_exploit(Strategy):
    def __init__(self, ratio: int, post_explore_updates: bool, num_balloons: int, db_path: str, game_id: int) -> None:
        super().__init__(name="Explore then Exploit", unrPnL=0, PnL=0, db_path=db_path)
        self.post_explore_updates = post_explore_updates
        self.ratio = ratio
        self.num_balloons = num_balloons
        self.game_id = game_id

    def unseen_color_handling(self, balloon: Balloon) -> str:
        # essentially assume a popping probability = 1/2
        return super().default_strat(balloon)
        
    def num_pumps(self, color: str) -> float:
        cur = self.conn.cursor()
        cur.execute(f"""SELECT balloon_color AS color, AVG(balloon_value)-1 as average_lifespan 
                    FROM game_{self.game_id} WHERE balloon_color = ?""", (color,))
        row = cur.fetchone()
        return row[1]
        
    
    def action(self, balloon: Balloon) -> str:

        cur = self.conn.cursor()
        cur.execute(f"SELECT COUNT(DISTINCT balloon_number) from game_{self.game_id}")
        db_size = cur.fetchone()[0]
        
        if db_size < self.num_balloons * self.ratio:
            # We are in Exploration Phase
            return "p" 
        else:
            # Exploitation phase
            cur.execute(f"SELECT DISTINCT balloon_color from game_{self.game_id}")
            seen_colors = cur.fetchall()
            if balloon.color not in seen_colors:
                self.unseen_color_handling(balloon)
            else:  
                average_lifespan = self.num_pumps(balloon.color) #Note: this is a float
                if balloon.value < np.floor(average_lifespan):
                    return "p"
                else:
                    return "c"
                
    def main(self, balloon) -> str:
        move = self.action(balloon, self.memory)
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
            
        




    

    
