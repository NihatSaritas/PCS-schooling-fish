import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd


# If run from main directory, appends 'validation/' to savepath.
PATH = ''


def animate(centroids, pikes, shiners):
    """
    Main animation loop. Saves small files as gif, big files as mp4.
    """
    fig, ax,  = plt.subplots(figsize=(12, 6))
    ax.set_xlim((0,200))
    ax.set_ylim((0,110))
    plt.title(f'Frame 0')
    frame_count = len(centroids)
    
    shiner = ax.quiver(shiners[0, :, 0], shiners[0, :, 1], shiners[0, :, 2], shiners[0, :, 3], color='lightblue', 
                       angles='xy', 
                       scale_units='xy',
                       scale=0.3,
                       label='shiner'
                    )

    centroid = ax.quiver(centroids[0, 0], centroids[0, 1], centroids[0, 2], centroids[0, 3], color='lightgreen',
                         angles='xy',
                         scale_units='xy',
                         scale=0.1,
                        label='centroid'
                        )

    pike = ax.quiver(pikes[0, 0], pikes[0, 1], pikes[0, 2], pikes[0, 3], color='red',
                     angles='xy',
                     scale_units='xy',
                     scale=0.2,
                     label='pike'
                    )

    plt.legend(loc = 'upper right', bbox_to_anchor=(1.125, 1))


    def update(frame_idx):
        """
        Update the arrows each frame with their new position and
        orientation. Repeat for each set of arrows.
        """
        plt.title(f'Frame {frame_idx}')
        centroid.set_offsets([[centroids[frame_idx, 0], centroids[frame_idx, 1]]])
        centroid.set_UVC(centroids[frame_idx, 2], centroids[frame_idx, 3])

        pike.set_offsets([[pikes[frame_idx, 0], pikes[frame_idx, 1]]])
        pike.set_UVC(pikes[frame_idx, 2], pikes[frame_idx, 3])

        frame_shiners = shiners[frame_idx,:,:]

        shiner.set_offsets(frame_shiners[:, :2])
        shiner.set_UVC(frame_shiners[:, 2], frame_shiners[:, 3])

    ani = FuncAnimation(
        fig,
        update,
        frames=frame_count,
        interval=500
    )

    ani.save(PATH + 'fish_animation_1.gif', writer='pillow', fps=2)
    plt.show()


def read_dataset(file):
    """
    Read csv file input and return pandas dataframe.
    """
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        global PATH
        PATH += 'validation/'
        df = pd.read_csv(PATH + file)
    df = df[['batch', 'id', 'x', 'y', 'hx', 'hy']]
    return df


def split_data(df):
    """
    Splits the dataset into positions and orientations for the fish, their centroid,
    and the predator. This allows to easily plot each of these in a different color.

    Makes assumption that the csv per frame always first contains the centroid, followed 
    by some number of fish, and lastly the pike (before showing the centroid of the next
    frame).
    
    Each frame contains a variable number of fish (shiners), and exactly 1 predator (pike).
    """
    frame_count = len(df[df['id'] == 'cnt'])
    centroids = []
    pikes = []
    # Larger than number of fish to serve as buffer since quiver can not handle varying 
    # number of fish. Unused slots are put on (5000,5000), which is off the grid.
    shiners = np.full((frame_count, 50, 4), [5000, 5000, 0, 0], dtype=np.float64)

    frame_counter = 0
    fish_counter = 0
    for _, row in df.iterrows():
        if row['id'] == 'cnt':  # First row of each frame
            centroids.append(row[['x', 'y', 'hx', 'hy']].values)
        elif row['id'] == 'PIKE':  # Final row of each frame
            pikes.append(row[['x', 'y', 'hx', 'hy']].values)
            frame_counter += 1
            fish_counter = 0
        else:
            shiners[frame_counter, fish_counter, :] = np.array(row[['x', 'y', 'hx', 'hy']].values)
            fish_counter += 1

    return np.array(centroids), np.array(pikes), shiners
            

def main():
    df = read_dataset('dataset1/final_movedat.csv')
    centroids, pikes, shiners = split_data(df)
    animate(centroids, pikes, shiners)


if __name__ == "__main__":
    main()
