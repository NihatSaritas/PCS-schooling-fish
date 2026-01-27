"""Headercomment here"""
# Get path to simulation file.
import sys
import os
root_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_folder)
from boids_hunteradams import BoidsVisualizer, Predator
import matplotlib.pyplot as plt
import time
import numpy as np

current_dir = root_folder + '/figure_scripts/'
save_path = current_dir + 'example1.png'


def cmd1(visualizer):
    """Make tank small and make fish look same direction to enforce schooling."""
    visualizer.sim.width=80
    visualizer.sim.height=80
    visualizer.sim.margin=10
    visualizer.resize()
    visualizer.sim.matching_factor = 1


def cmd1_undo(visualizer):
    """Go back to default values and (hopefully) fish will all be schooling."""
    visualizer.sim.width=640
    visualizer.sim.height=480
    visualizer.sim.margin=128
    visualizer.resize()
    visualizer.sim.matching_factor = 0.05

def cmd2(visualizer):
    """Initialize a predator entering from bottomright corner."""
    x = 630
    y = 470
    vx = 0
    vy = 0
    visualizer.sim.predators.append(Predator(x,y,vx,vy))
    visualizer.sim.num_preds = 1
    visualizer.edit_pred_count()

if __name__ == "__main__":
    fake_image = [[40]]
    repetitions = 5
    results = []

    for i in range(repetitions):
        # Create visualizer (does NOT block)
        seed = 123+i
        print(f"Running seed: {seed}... ", end='')
        visualizer = BoidsVisualizer(num_boids=50, num_preds=0, width=640, height=480, seed=seed, pause_after=2)
        visualizer.delay=1

        print(f"Enforcing schooling behavior... ", end='')
        cmd1(visualizer)
        visualizer.resume(pause_after=25)

        print("Resetting tank size... ", end="")
        cmd1_undo(visualizer)
        visualizer.resume(pause_after=10)

        print("Spawn in predator.")
        cmd2(visualizer)
        visualizer.resume(6000)

        # Resume for another 1000 frames, then save relevant data, then close visualizer.
        survived = visualizer.sim.num_boids
        results.append(survived)
        visualizer.close()
        visualizer = None  # dereference to throw out of memory, not really needed
        print(f"{survived} fish managed to stay alive!")

    print(np.mean(results))
