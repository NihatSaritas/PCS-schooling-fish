""" This particular dataset does not store orientations, but we instead use the
stored velocity in x and y direction as orientation of the fish.

TODO: explain used paper and refer to its method of computing polarization and 
the milling index."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
import json as json


# If run from main directory, appends 'validation/' to savepath.
PATH = ''
# Buffersize for quiver to handle inconsistent tracked number of fish.
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


def frame_behavior_quantification(framedata, polarization=True, milling_index=True):  # dispersion=False,
    # Compute the polarization. See header comment for details.
    px, py, vx, vy, count = framedata
    px = px[0:count]
    py = py[0:count]
    vx = vx[0:count]
    vy = vy[0:count]

    d = np.column_stack([vx, vy])
    lengths = np.linalg.norm(d, axis=1, keepdims=True)
    dnorm = d / lengths
    polarization = np.linalg.norm(np.mean(dnorm, axis=0))

    # Compute the milling index. See header comment for details.
    p = np.column_stack([px, py])
    barycenter = np.mean(p, axis=0)
    xbar = px - barycenter[0]
    ybar = py - barycenter[1]
    theta = np.atan2(ybar, xbar)

    barycenter_d = np.mean(d, axis=0)
    barvx = vx - barycenter_d[0]
    barvy = vy - barycenter_d[1]
    phi = np.atan2(barvy, barvx)

    milling_index = np.abs(np.mean(np.sin(phi - theta)))

    return polarization, milling_index


def create_hist(p, m):
    bins=50

    for end in [-1, 2500]:
        fig = plt.figure()
        plt.hist(p[0:end], bins, alpha=0.5, label='polarization', color='b', density=True)
        plt.hist(m[0:end], bins, alpha=0.5, label='milling index', color='r', density=True)
        plt.legend(loc='upper right')
        if end == -1:
            plt.savefig(PATH + 'dataset_hist_full.png')
        else:
            plt.savefig(PATH + 'dataset_hist.png')
        plt.show()




def animate(fish_dict):
    """
    Main animation loop. Saves small files as gif, big files as mp4.
    """
    frame_count = len(fish_dict)
    # frame_count = 20
    # Initialize figure, set the first frame.
    # fig = plt.figure(figsize=(12, 10))
    fig, axes = plt.subplot_mosaic("A;A;B", figsize=(12, 10))
    ax = axes["A"]
    ax_sub = axes["B"]

    ax.set_xlim((0,2100))
    ax.set_ylim((0,1200))
    ax_sub.set_xlim(0, frame_count)
    ax_sub.set_ylim(0, 1)

    ax_sub.set_xlabel('Frame')
    ax_sub.set_ylabel('Polarization / Milling index')


    polarization, milling = frame_behavior_quantification(split_data(fish_dict,1))
    x = [1]
    p = [polarization]
    m = [milling]

    stem_polarization = ax_sub.stem(x, p, basefmt='b', linefmt=None, markerfmt='b')
    stem_milling = ax_sub.stem(x, m, basefmt='r', linefmt=None, markerfmt='r')
    stem_polarization[1].set_visible(False)
    stem_polarization[2].set_visible(False)
    stem_milling[1].set_visible(False)
    stem_milling[2].set_visible(False)

    plt.setp(stem_polarization[0], markersize=2, alpha=0.2, color='b')
    plt.setp(stem_milling[0], markersize=2, alpha=0.2, color='r')

    px, py, vx, vy, count = split_data(fish_dict, 1)
    ax.set_title(f'Frame 1, tracked fish: {count}')

    fish = ax.quiver(px, py, vx, vy, color='orange', 
                       angles='xy', 
                       scale_units='xy',
                       label='golden\nshiner',
                    )

    ax.legend(loc = 'upper right', bbox_to_anchor=(1.125, 1))

    # Low opacity (alpha) value for markers makes the legend unreadable, this workaround
    # creates a custom legend with visible colorcoding.
    custom_legend = [Line2D([0], [0], color='b', lw=1), Line2D([0], [0], color='r', lw=1)]
    ax_sub.legend(custom_legend, ['polarization', 'milling\nindex'], loc = 'upper right', bbox_to_anchor=(1.125, 1))

    def update(frame_idx):
        """
        Update the arrows each frame with their new position and
        orientation.
        """
        frame = frame_idx + 1
        px, py, vx, vy, count = split_data(fish_dict, frame)
        polarization, milling = frame_behavior_quantification([px, py, vx, vy, count])
        ax.set_title(f'Frame {frame}, tracked fish: {count}')

        fish.set_offsets(np.column_stack((px, py)))
        fish.set_UVC(vx, vy)

        if frame_idx not in x:
            x.append(frame_idx)
            p.append(polarization)
            m.append(milling)

            stem_polarization[0].set_xdata(x)
            stem_polarization[0].set_ydata(p)

            #stem_polarization[2].set_xdata(x)
            #stem_polarization[2].set_ydata(p)

        
            stem_milling[0].set_xdata(x)
            stem_milling[0].set_ydata(m)

            #stem_milling[2].set_xdata(x)
            #stem_milling[2].set_ydata(m)


    ani = FuncAnimation(
        fig,
        update,
        frames=frame_count,
        interval=1
    )

    # Saving as gif is very slow and large (200+ mb) for 5000 frames, 
    # so switch to video format instead.
    # ani.save('fish_animation_2.gif', writer='pillow', fps=60)
    ani.save(PATH + 'fish_animation_2_with_quant.mp4', writer='ffmpeg', fps=60)
    plt.show()
    create_hist(p, m)


def read_dataset(file):
    try:
        f = open(file)
    except FileNotFoundError:
        global PATH
        PATH += 'validation/'
        f = open(PATH + file)
    file_content = f.read()
    fish_dict = json.loads(file_content)
    return fish_dict


def main():
    fish_dict = read_dataset('dataset2/schooling_frames.json')
    animate(fish_dict)


if __name__ == "__main__":
    main()
