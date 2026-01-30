"""Create histogram of polarization and milling index over 10 iterations for
2000 frames."""

# Get path to simulation file.
import matplotlib.pyplot as plt
from boids_hunteradams import BoidsVisualizer
import sys
import os

root_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_folder)
# import time

current_dir = root_folder + "/figure_scripts/"
HEIGHT = 350
WIDTH = 350
DURATION = 2000
ITERATIONS = 10


def enforce_schooling(visualizer):
    """Make tank small and make fish look same direction to enforce schooling."""
    visualizer.sim.width = 120
    visualizer.sim.height = 120
    visualizer.sim.margin = 10
    visualizer.resize()
    visualizer.sim.matching_factor = 1


def set_params(visualizer):
    """Go back to (tweaked) default values. The changes attempt to nudge behavior
    in the direction that better matches the behavior seen in dataset2, since of
    each species of fish will be different to some extent."""
    visualizer.sim.width = WIDTH
    visualizer.sim.height = HEIGHT
    visualizer.sim.margin = 50
    visualizer.resize()
    visualizer.sim.matching_factor = 0.05

    visualizer.sim.maxspeed = 3 * 0.45
    visualizer.sim.minspeed = 2 * 0.45
    visualizer.sim.turn_factor = 0.15 * 1.3  # you are different, should be 0.15*1.3
    visualizer.sim.protected_range *= 1.25
    visualizer.sim.avoid_factor *= 1.6
    visualizer.sim.matching_factor *= 1.1
    visualizer.sim.front_weight = 2
    visualizer.sim.max_turn *= 1.5
    visualizer.sim.centering_factor *= 1.5
    visualizer.sim.visual_range /= 1.2


if __name__ == "__main__":
    p = []
    m = []
    seed = "5062PRCS6Y"

    for i in range(ITERATIONS):
        # Create visualizer (does NOT block)
        print(f"Running seed: {seed}... ", end="")
        visualizer = BoidsVisualizer(
            num_boids=200,
            num_preds=0,
            width=WIDTH,
            height=HEIGHT,
            seed=seed + str(i),
            pause_after=2,
        )
        visualizer.delay = 1

        print("Enforcing schooling behavior... ", end="")
        enforce_schooling(visualizer)
        visualizer.resume(pause_after=25)

        print("Resetting tank size... ", end="")
        set_params(visualizer)
        visualizer.resume(pause_after=100)

        visualizer.toggle_stats()
        visualizer.stat_xrange = DURATION
        visualizer.stats.resize()
        visualizer.resume(DURATION)
        visualizer.stats.fig.savefig(current_dir + "validate_simulation.png")

        p.extend(visualizer.stats.polarization)
        m.extend(visualizer.stats.milling_index)
        visualizer.close()

    bins = 50

    fig = plt.figure()
    plt.hist(p, bins, alpha=0.5, label="polarization", color="b", density=True)
    plt.hist(m, bins, alpha=0.5, label="milling index", color="r", density=True)
    plt.legend(loc="upper right")
    if plt.ylim()[1] < 3.5:
        plt.ylim(0, 3.5)
    fig.savefig(current_dir + "simulation_hist.png")
    plt.show()

    # visualizer = None
    print(f"Saved file to {current_dir + 'validate_simulation.png'}")
