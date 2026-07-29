
from simple_strategies import explore_then_exploit, constant_pump
from Classes import Game


Game.clear_game(3)
my_strat = explore_then_exploit(0.25, 100, 3, 1)
my_strat2 = constant_pump(3)
my_game = Game([my_strat, my_strat2], 100, 3)

my_game.start()
my_game.print_summary(3)













