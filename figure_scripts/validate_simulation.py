"""Headercomment here"""
# Get path to simulation file.
import sys
import os
root_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_folder)
from boids_hunteradams import BoidsVisualizer, Predator
#import matplotlib.pyplot as plt
#import time
import numpy as np

current_dir = root_folder + '/figure_scripts/'
save_path = current_dir + 'validate_simulation.png'
HEIGHT = 400
WIDTH = 400
DURATION = 1000

def cmd1(visualizer):
    """Make tank small and make fish look same direction to enforce schooling."""
    visualizer.sim.width=80
    visualizer.sim.height=80
    visualizer.sim.margin=10
    visualizer.resize()
    visualizer.sim.matching_factor = 1


def cmd1_undo(visualizer):
    """Go back to default values and (hopefully) fish will all be schooling."""
    visualizer.sim.width=WIDTH
    visualizer.sim.height=HEIGHT
    visualizer.sim.margin=80
    visualizer.resize()
    visualizer.sim.matching_factor = 0.05 #0.05
    visualizer.sim.maxspeed = 3
    visualizer.sim.minspeed = 2
    visualizer.sim.turn_factor = 0.3
    visualizer.sim.max_turn = 0.3


def open_stats(visualizer):
    pass

if __name__ == "__main__":
    fake_image = [[40]]
    repetitions = 5
    results = []

    # Create visualizer (does NOT block)
    seed = 123
    print(f"Running seed: {seed}... ", end='')
    visualizer = BoidsVisualizer(num_boids=250, num_preds=0, width=WIDTH, height=HEIGHT, seed=seed, pause_after=2)
    visualizer.delay=1

    print(f"Enforcing schooling behavior... ", end='')
    cmd1(visualizer)
    visualizer.resume(pause_after=25)

    print("Resetting tank size... ", end="")
    cmd1_undo(visualizer)
    visualizer.resume(pause_after=10)

    visualizer.toggle_stats()
    visualizer.stat_xrange = DURATION
    visualizer.stats.resize()
    visualizer.resume(DURATION)
    visualizer.stats.fig.savefig(save_path)
    visualizer.close()
    #visualizer = None
    print(f"Saved file to {save_path}")
