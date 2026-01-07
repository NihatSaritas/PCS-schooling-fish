import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def draw_frame():
    pass

def dummy_frames():
    frames = np.zeros((2,2,1000))
    frames[:,:,0] = np.array([[1,0.5],[1,1.5]])
    for i in range(1,1000):
        frames[:,:,i] = frames[:,:,i-1] + np.array([[0.01,0.01],[0,0]])

    return frames

def animate():
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim((0,15))
    ax.set_ylim((0,2))
    frames = dummy_frames()
    # plt.quiver([1,0.5],[1,1.5],[1,1],[0,0])
    Q = ax.quiver(
            frames[:, :, 0][0], frames[:, :, 0][1], [1, 1],[0, 0],
            # angles='xy',
            # scale_units='xy',
            # scale=1
        )
    
    def update(frame_idx):
        # Set new positions for vectors, each timestep moves 0.01 to the right (see dummy generated frame.)
        Q.set_offsets(np.c_[frames[:, :, frame_idx][0],
                            frames[:, :, frame_idx][1]])
        # Set direction, static in this example but will be needed later
        Q.set_UVC([1, 1],[0, 0])

    ani = FuncAnimation(
        fig,
        update,
        frames=frames.shape[2],
        interval=5
    )

    plt.show()
    #plt.savefig('tmp')

def main():
    print('main')
    animate()
    

if __name__ == "__main__":
    main()