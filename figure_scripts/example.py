"""Headercomment here"""
# Get path to simulation file.
import sys
import os
root_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_folder)
from boids_hunteradams import BoidsVisualizer, Predator
import matplotlib.pyplot as plt
import time

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
    plt.imsave(save_path, fake_image)

    # Create visualizer (does NOT block)
    visualizer = BoidsVisualizer(num_boids=50, num_preds=0, width=640, height=480, seed=123, pause_after=1) 
    # remember to increment seed if repeating and taking average or whatever, set seed=None for random seeds while testing (final figures should not be random)
    print("Stop after frame 26 to resize and do... nothing")
    time.sleep(1)  # not needed but for visual clarity since this is an example

    visualizer.resume(pause_after=25)
    print("Stop after frame 26 to resize and change params to match directions fast")
    cmd1(visualizer)
    time.sleep(1)  # not needed but for visual clarity since this is an example

    visualizer.resume(pause_after=50)
    print("Stop after frame 76 undo tank size change and undo change to matching directions")
    cmd1_undo(visualizer)
    time.sleep(1)  # not needed but for visual clarity since this is an example

    visualizer.resume(pause_after=15)
    print("Stop after frame 91 and add predator to bottomright corner")
    cmd2(visualizer)
    time.sleep(1)  # not needed but for visual clarity since this is an example

    # do this to resume indefinitely
    # visualizer.resume()  

    # or do this to resume for another 1000 frames, then save relevant data, then close visualizer.
    visualizer.resume(pause_after=1000)
    survived = visualizer.sim.num_boids
    visualizer.close()
    visualizer = None  # dereference to throw out of memory, not really needed
    print(f"{survived} fish managed to stay alive!")
