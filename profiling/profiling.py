
"""
This part of the profiling is finding out which function is the bottleneck 
NOTE: profiling modules take time so only trust the relative times between functions


"""


import cProfile
import pstats
from harness import run_game
from record_harness import save_profiler

NUM_BALLOONS = 150

def main():
    profiler = cProfile.Profile()
    profiler.enable()
    run_game(tag="profiling", num_balloons=NUM_BALLOONS)
    profiler.disable()
    save_profiler(profiler, NUM_BALLOONS)


    stats = pstats.Stats(profiler)
    stats.strip_dirs()

    
    print("SORTED BY cumtime  - which BRANCH of the program is expensive?")
    stats.sort_stats("cumulative").print_stats(10) # Only shows top 10 

    
    print("SORTED BY tottime  - which SINGLE FUNCTION is expensive?")
    stats.sort_stats("tottime").print_stats(10)
    

if __name__ == "__main__":
    main()