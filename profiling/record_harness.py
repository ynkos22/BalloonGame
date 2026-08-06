
import cProfile
import json, os, subprocess
from datetime import datetime
# This module records profiling logs to compare later


RESULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "runs.jsonl")


# Returns the most recent commit
def get_commit() -> str:
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return sha

    
# This adds a profiling row to the JSONL
def append_record(record: dict) -> None:
    os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True) # Make a results folder if it doesn't exist
    with open(RESULT_PATH, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record) + "\n")


# Saves a profiler to a .prof file
def save_profiler(profiler: cProfile.Profile, num_balloons: int) -> None:
    # saves the .prof file
    sha = get_commit()
    prof_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(prof_dir, exist_ok=True)
    prof_path = os.path.join(prof_dir, f"{sha}_{num_balloons}.prof")
    profiler.dump_stats(prof_path)

    # logs into jsonl
    record = { 
        "commit": sha,
        "script": "profiling",
        "prof_file": os.path.basename(prof_path),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    append_record(record)
    
    





