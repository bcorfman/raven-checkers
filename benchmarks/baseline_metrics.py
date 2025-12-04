# Sets up a Checkers game in some fixed positions.
# Calls alphabeta_search at various depths.
# After each call, reads game.last_search_stats and appends it to a CSV file

import csv
from game.checkers import Checkers
import ai.games as games

print("Running baseline_metrics...") 

game = Checkers()
state = game.curr_state

with open("baseline_search_metrics.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "algorithm", "depth_limit", "max_depth_reached",
        "nodes_expanded", "runtime_sec"
    ])
    writer.writeheader()

    for d in range(1, 9):
        action = games.alphabeta_search(state, game, d)
        stats = game.last_search_stats
        stats["algorithm"] = "baseline_alphabeta"

        print(f"Depth {d}: {stats}")

        writer.writerow(stats)
