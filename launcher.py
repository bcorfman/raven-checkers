#!/usr/bin/env python
"""
Launcher to control which search algorithm to use

Commands to use:
python launcher.py                  # DEFAULT - uses alphabeta
python launcher.py spark            # Uses Spark
python launcher.py minimax          # Uses minimax
python launcher.py spark -m        # Uses Spark with metrics
"""

import sys
import ai.algorithm_config as config

# parse arguments from command line
if len(sys.argv) > 1:
    algorithm = sys.argv[1].lower()
    if algorithm in ['alphabeta', 'minimax', 'spark']:
        config.ALGORITHM = algorithm
    else:
        print(f"Unknown algorithm: {algorithm}")
        print("Use: alphabeta, minimax, or spark")
        sys.exit(1)

if '-m' in sys.argv:
    config.ENABLE_METRICS = True

# Display configurations
print(f"Start Checkers game with {config.ALGORITHM.upper()} algorithm")
if config.ENABLE_METRICS:
    print("Performance metrics: ENABLED")
print()

# Start the game
import main
main.start()
