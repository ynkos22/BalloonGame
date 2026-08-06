

"""
This part of the profiling assesses how well the code scales.

This is to reveal algorithmic asymptotic bottlenecks.

"""
from record_harness import get_commit, append_record
import time
from datetime import datetime
from harness import run_game, count_turns
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

        # saves the record to jsonl
        sha = get_commit()
        result = {
            "commit": sha,
            "script": "scaling",
            "n_size": n,
            "wall_time": w_time, 
            "ms_per_turn": ms_per_turn,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        }
        append_record(result)
        print(f"scale: {n}, wall_time = {w_time:6.2f}, ms_per_turn = {ms_per_turn: 6.2f}")



if __name__ == "__main__":
    main()
