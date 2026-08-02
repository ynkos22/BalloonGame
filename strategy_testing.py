
from simple_strategies import explore_then_exploit, constant_pump, thompson_sampling
from Classes import Game



my_strat = explore_then_exploit(0.25, 1000, 5, 1)
my_strat2 = constant_pump(4)
my_strat3 = thompson_sampling(5)
my_game = Game([my_strat, my_strat2, my_strat3], 1000, 5)

my_game.start()
my_game.print_summary(5)













