"""TODO: header comment."""
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
import numpy as np


MARKER_ALPHA = 0.2
LINE_ALPHA = 0.1


class StatWindow:
    def __init__(self, visualizer):
        self.visualizer = visualizer

        # Setup tkinter window for stats.
        self.stats_win = tk.Toplevel(visualizer.root)
        self.stats_win.title("Boids Stats")
        self.stats_win.geometry("800x400")

        # Setup Matplotlib figure.
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim((0,1))
        self.ax.set_xlim((self.visualizer.frame, self.visualizer.frame+self.visualizer.stat_xrange))

        self.ax.set_ylabel("Polarization / Milling Index")
        self.ax.set_xlabel("Frame number")

        # Create stems with dummy point to prevent initialization error. 
        self.stem_polarization = self.ax.stem([-10], [0], basefmt='b', linefmt=None, markerfmt='b')
        self.stem_milling = self.ax.stem([-10], [0], basefmt='r', linefmt=None, markerfmt='r')
        self.stem_polarization[1].set_visible(False)
        #self.stem_polarization[2].set_visible(False)
        self.stem_milling[1].set_visible(False)
        #self.stem_milling[2].set_visible(False)

        # Set markerstyle and manual legend (needed for readability).
        self.stem_polarization[0].set_markersize(2)
        self.stem_polarization[0].set_alpha(MARKER_ALPHA)
        self.stem_polarization[0].set_color('b')

        self.stem_milling[0].set_markersize(2)
        self.stem_milling[0].set_alpha(MARKER_ALPHA)
        self.stem_milling[0].set_color('r')

        self.stem_polarization[2].set_alpha(LINE_ALPHA)
        self.stem_polarization[2].set_color('b')

        self.stem_milling[2].set_alpha(LINE_ALPHA)
        self.stem_milling[2].set_color('r')


        custom_legend = [Line2D([0], [0], color='b', lw=1), Line2D([0], [0], color='r', lw=1)]
        self.ax.legend(custom_legend, ['polarization', 'milling\nindex'], loc = 'upper right', bbox_to_anchor=(1.125, 1))

        # Embed Matplotlin figure in Tkinter window.
        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=self.stats_win)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Setup datastructures for plotting data.
        self.x = []
        self.polarization = []
        self.milling_index = []

        self.stats_win.protocol("WM_DELETE_WINDOW", self.visualizer.toggle_stats)


    def resize(self):
        """Function in other subclass updates the xrange. This function resizes
        the datastructures accordingly."""
        self.ax.set_xlim((self.x[0] if self.x else 1, max(self.x[0] + self.visualizer.stat_xrange, self.x[-1])))
        if len(self.x) > self.visualizer.stat_xrange:
            drop_first_n = len(self.x) - self.visualizer.stat_xrange
            self.x = self.x[drop_first_n:]
            self.polarization = self.polarization[drop_first_n:]
            self.milling_index = self.milling_index[drop_first_n:]

    def update(self):
        px, py, vx, vy = self.visualizer.sim.get_states()

        # Compute the polarization. See README for details.
        d = np.column_stack([vx, vy])
        lengths = np.linalg.norm(d, axis=1, keepdims=True)
        dnorm = d / lengths
        polarization = np.linalg.norm(np.mean(dnorm, axis=0))

        # Compute the milling index. See README for details.
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

        # Update data structures
        self.x.append(self.visualizer.frame)
        self.polarization.append(polarization)
        self.milling_index.append(milling_index)
        if len(self.x) > self.visualizer.stat_xrange:
            # Make sliding window after full xrange.
            self.x.pop(0)
            self.polarization.pop(0)
            self.milling_index.pop(0)
            self.ax.set_xlim((self.x[0], self.x[-1]))

        # Replot figure and draw on canvas.
        self.stem_polarization[0].set_xdata(self.x)
        self.stem_polarization[0].set_ydata(self.polarization)
        self.stem_polarization[2].set_xdata(self.x)
        self.stem_polarization[2].set_ydata(self.polarization)

        self.stem_milling[0].set_xdata(self.x)
        self.stem_milling[0].set_ydata(self.milling_index)
        self.stem_milling[2].set_xdata(self.x)
        self.stem_milling[2].set_ydata(self.milling_index)

        self.fig_canvas.draw()

    def close(self):
        """Destroy window and dereference object."""
        self.stats_win.destroy()
        self.stats_win = None

if __name__ == "__main__":
    print("This file is not meant to be run directly. Refer to the README for details.")
