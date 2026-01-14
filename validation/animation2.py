""" This particular dataset does not store orientations, but we instead use the
stored velocity in x and y direction as orientation of the fish."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json as json


NUM_FISH = 300


def split_data(fish_dict, frame):
    """
    Extract data corresponding to certain framenumber, then split
    into position and orientations.

    For our animation we use the quiver method and update the arrow
    positions and orientations. This requires a constant number of
    fish in each frame. The number of fish tracked in each frame
    fluctuates. This is resolved by using a 300 fish buffer for
    the quiver, and moving untracked fish to a position off the
    grid (5000, 5000).

    Lastly, explicitly storing the data as floats in an array is
    required to resolve an error with the animation loop internally
    calling the function np.isfinite().
    """
    frame_data = fish_dict[f"{frame}"]
    px = np.asarray(frame_data["px"], dtype=np.float64)
    py = np.asarray(frame_data["py"], dtype=np.float64)
    vx = np.asarray(frame_data["vx"], dtype=np.float64)
    vy = np.asarray(frame_data["vy"], dtype=np.float64)

    count = len(px)
    if count < NUM_FISH:
        pad_len = NUM_FISH - count
        px = np.pad(px, (0, pad_len), constant_values=5000)
        py = np.pad(py, (0, pad_len), constant_values=5000)
        vx = np.pad(vx, (0, pad_len), constant_values=0)
        vy = np.pad(vy, (0, pad_len), constant_values=0)

    return px, py, vx, vy, count


def animate(fish_dict):
    """
    Main animation loop. Saves small files as gif, big files as mp4.
    """
    # Initialize figure, set the first frame.
    fig, ax,  = plt.subplots(figsize=(12, 6))
    ax.set_xlim((0,2100))
    ax.set_ylim((0,1200))
    frame_count = len(fish_dict)
    
    px, py, vx, vy, count = split_data(fish_dict, 1)
    plt.title(f'Frame 1, tracked fish: {count}')

    fish = ax.quiver(px, py, vx, vy, color='orange', 
                       angles='xy', 
                       scale_units='xy',
                       label='golden\nshiner',
                    )

    plt.legend(loc = 'upper right', bbox_to_anchor=(1.125, 1))


    def update(frame_idx):
        """
        Update the arrows each frame with their new position and
        orientation.
        """
        frame = frame_idx + 1
        px, py, vx, vy, count = split_data(fish_dict, frame)
        plt.title(f'Frame {frame}, tracked fish: {count}')

        fish.set_offsets(np.column_stack((px, py)))
        fish.set_UVC(vx, vy)

    ani = FuncAnimation(
        fig,
        update,
        frames=frame_count,
        interval=2
    )

    # Saving as gif is very slow and large (200+ mb) for 5000 frames, 
    # so switch to video format instead.
    # ani.save('fish_animation_2.gif', writer='pillow', fps=60)
    ani.save('fish_animation_2.mp4', writer='ffmpeg', fps=60)
    plt.show()


def read_dataset(file):
    try:
        f = open(file)
    except FileNotFoundError:
        f = open('validation/' + file)
    file_content = f.read()
    fish_dict = json.loads(file_content)
    return fish_dict


def main():
    fish_dict = read_dataset('dataset2/schooling_frames.json')
    animate(fish_dict)


if __name__ == "__main__":
    main()
