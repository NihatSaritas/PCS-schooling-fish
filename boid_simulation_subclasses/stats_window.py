"""This file contains the class for stats window of the visualizer, see its documentation
in the class comment below. It is intened to be used by the visualizer, do not run this 
file directly."""
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
import numpy as np


# Styling globals for figure
MARKER_ALPHA = 0.2
LINE_ALPHA = 0.1


class StatWindow:
    """Class for visualizing the polarization and milling-index over time while a simulation and its
    visualization class are running. For definitions on these metrics refer to the report. Uses a
    Matplotlib stemplot to create the figure and embeds this in a tkinter window. When the default
    x-range (2000) fills, the window slides by 1 each frame. The width of this x-range is configurable
    in the settings window.
    
    Args:
        visualizer: serves as reference to parent visualizer, which holds a reference to the simulation,
                    which is called to compute and return the polarization and milling-index.
    """
    def __init__(self, visualizer):
        # Reference to parent, needed to access the polarization and milling-index.
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
        self.stem_milling[1].set_visible(False)

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

        # Handle closing window with x in the same way as a toggle-off click would have, i.e. it
        # turns the stats window button red.
        self.stats_win.protocol("WM_DELETE_WINDOW", self.visualizer.toggle_stats)

    def resize(self):
        """Function in other subclass updates the x range of the sliding window. 
        This function resizes the datastructures accordingly."""
        # The if else statements handle cases where the x-range is edited without the stats window being open.
        # The max function handles choosing the proper upper limit for xlim. TODO
        self.ax.set_xlim((self.x[0] if self.x else 1, 
                          max(self.x[0] + self.visualizer.stat_xrange, self.x[-1]) if self.x else self.visualizer.stat_xrange))
        if len(self.x) > self.visualizer.stat_xrange:
            drop_first_n = len(self.x) - self.visualizer.stat_xrange
            self.x = self.x[drop_first_n:]
            self.polarization = self.polarization[drop_first_n:]
            self.milling_index = self.milling_index[drop_first_n:]

    def update(self):
        polarization, milling_index = self.visualizer.sim.get_stats()

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
