

"""
This part of the profiling assesses how well the code scales.

This is to reveal algorithmic asymptotic bottlenecks.

"""

import time
from harness import run_game, count_turns, fresh_db
import os
import tempfile

SIZES = (50, 100, 200, 400)


def main():

    for n in SIZES:
        w_time = time.perf_counter()
        db = run_game(tag = "scaling", num_balloons=n)
        w_time = time.perf_counter() - w_time

        num_turns = count_turns(db)
        ms_per_turn = 1000 * w_time/num_turns

        print(f"scale: {n}, wall_time = {w_time:6.2f}, ms_per_turn = {ms_per_turn: 6.2f}")



if __name__ == "__main__":
    main()
