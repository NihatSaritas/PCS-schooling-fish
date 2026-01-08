import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

def draw_frame():
    pass

def dummy_frames():
    frames = np.zeros((2,2,1000))
    frames[:,:,0] = np.array([[1,0.5],[1,1.5]])
    for i in range(1,1000):
        frames[:,:,i] = frames[:,:,i-1] + np.array([[0.01,0.01],[0,0]])

    return frames

def animate(centroids, pikes, shiners):
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

    ani.save('fish_animation.gif', writer='pillow', fps=2)
    plt.show()

    #plt.savefig('tmp')

def read_dataset(file):
    df = pd.read_csv(file)
    #print(df.columns)
    df = df[['batch', 'id', 'x', 'y', 'hx', 'hy']]
    #print(df.columns)
    return df

def split_data(df):
    frame_count = len(df[df['id'] == 'cnt'])
    centroids = []
    pikes = []
    shiners = np.zeros((frame_count, 50, 4))

    frame_counter = 0
    fish_counter = 0
    for _, row in df.iterrows():
        if row['id'] == 'cnt':
            centroids.append(row[['x', 'y', 'hx', 'hy']].values)
        elif row['id'] == 'PIKE':
            pikes.append(row[['x', 'y', 'hx', 'hy']].values)
            frame_counter += 1
            fish_counter = 0
        else:
            shiners[frame_counter, fish_counter, :] = np.array(row[['x', 'y', 'hx', 'hy']].values)
            fish_counter += 1

    return np.array(centroids), np.array(pikes), shiners
            

def main():
    print('main')
    df = read_dataset('dataset1/final_movedat.csv')
    print(f'xlim ({df['x'].min()}, {df['x'].max()})')
    print(f'ylim ({df['y'].min()}, {df['y'].max()})')

    # centroids = df[df['id'] == 'cnt']
    # pikes = df[df['id'] == 'PIKE']
    # cts1 = centroids[centroids['batch'] == 1]
    # pks1 = pikes[pikes['batch'] == 1]

    centroids, pikes, shiners = split_data(df)
    # print(len(pks1))
    # print(len(cts1))
    animate(centroids, pikes, shiners)


if __name__ == "__main__":
    main()
