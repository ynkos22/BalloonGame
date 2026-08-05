

"""
This script should give a rough idea of how long the program takes to run end-to-end
This includes wall-time and cpu-time


"""
import time
from harness import run_game
NUMBER_BALLOONS = 150
TRIALS = 3


def main():
    print(f"Workload: {NUMBER_BALLOONS} balloons x 3 strategies, repeated {TRIALS} times")

    wall_times, cpu_times = [], []
    for i in range(TRIALS):
        w_time, cpu_time = time.perf_counter(), time.process_time()
        run_game(tag="total_time", num_balloons=NUMBER_BALLOONS)
        w = time.perf_counter() - w_time
        cpu = time.process_time() - cpu_time
        wall_times.append(w)
        cpu_times.append(cpu)

        print(f" run {i}, wall_time: {w: 6.2f}, processing_time: {cpu: 6.2f}")

    best_wtime = min(wall_times)
    best_cputime = min(cpu_times)
    waiting_time = best_wtime - best_cputime

    print(f"best wall time = {best_wtime: 6.2f}")
    print(f"best processing time = {best_cputime: 6.2f}")
    print(f"waiting time = {waiting_time: 6.2f} ({100*waiting_time/best_wtime: 6.2f} % of total)")

    





if __name__ == "__main__":
    main()