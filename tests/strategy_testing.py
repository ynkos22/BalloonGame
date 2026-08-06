import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simple_strategies import explore_then_exploit, constant_pump, thompson_sampling, benchmark
from Classes import Game

game_num = 24
total_balloons = 1000

my_strat = explore_then_exploit(0.05, total_balloons, game_num, 2)
my_strat2 = constant_pump(4)
my_strat3 = thompson_sampling(game_num)
my_strat4 = benchmark()
my_game = Game([my_strat, my_strat2, my_strat3, my_strat4], total_balloons, game_num)

my_game.start()
my_game.print_summary(game_num)













