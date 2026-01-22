import math
import random
import tkinter as tk
import numpy as np
import signal
import sys
from boid_simulation_subclasses.stats_window import StatWindow
from boid_simulation_subclasses.settings_window import SettingsWindow

class Boid:
    """Represents a single fish/boid in the simulation."""
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

class Predator:
    """Represents a single predator in the simulation."""

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

class BoidsSimulation:
    def __init__(self, num_boids=50, num_preds=1, width=640, height=480):
        # Tunable parameters
        self.num_boids = num_boids
        self.turn_factor = 0.2
        self.visual_range = 40
        self.protected_range = 8
        self.centering_factor = 0.0005
        self.avoid_factor = 0.07
        self.matching_factor = 0.05
        self.maxspeed = 3
        self.minspeed = 2

        # Predator parameters
        self.turn_factor_pred = 0.2
        self.predatory_range = 100
        self.maxspeed_pred = 3
        self.minspeed_pred = 2
        self.predator_weight = 0.1

        """Inspired additions by Katz-et-all"""
        self.fieldofview_degrees = 170 # small blind zone behind
        self.fieldofview = math.cos(math.radians(self.fieldofview_degrees))
        self.front_weight = 0.3
        self.speed_control = 0.03
        self.turning_control = 0.05
        self.max_turn = 0.15

        # Screen dimensions
        self.width = width
        self.height = height

        # Margins for turning
        self.margin = max(0.2 * width, 0.2 * height)
        self.leftmargin = self.margin
        self.rightmargin = width - self.margin
        self.topmargin = self.margin
        self.bottommargin = height - self.margin

        # Precompute squared ranges for efficiency
        self.visual_range_squared = self.visual_range * self.visual_range
        self.protected_range_squared = self.protected_range * self.protected_range

        # Initialize boids with random positions and velocities
        self.boids = []
        for _ in range(num_boids):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            vx = random.uniform(-self.maxspeed, self.maxspeed)
            vy = random.uniform(-self.maxspeed, self.maxspeed)
            self.boids.append(Boid(x, y, vx, vy))

        # Initialize predators with random positions and velocities
        self.predators = []
        for _ in range(num_preds):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            vx = random.uniform(-self.maxspeed_pred, self.maxspeed_pred)
            vy = random.uniform(-self.maxspeed_pred, self.maxspeed_pred)
            self.predators.append(Predator(x, y, vx, vy))

    def edit_boid_count(self):
        """Removes or adds boids until number of boids match the (edited) parameter. Additions
        are random. Removal is deterministic and depends on the index in self.boids."""
        while(len(self.boids) < self.num_boids):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            vx = random.uniform(-self.maxspeed, self.maxspeed)
            vy = random.uniform(-self.maxspeed, self.maxspeed)
            self.boids.append(Boid(x, y, vx, vy))

        if len(self.boids) > self.num_boids:      
            self.boids = self.boids[0:self.num_boids]

    def edit_fov(self):
        """Subwindow updates FOV in degrees. This function is called to update the parameter."""
        self.fieldofview = math.cos(math.radians(self.fieldofview_degrees))
        print(f'fov:{self.fieldofview_degrees}° -> {self.fieldofview}')

    def update(self):
        """Update all boids and predators for one timestep"""
        for boid in self.boids:
            # Heading frame
            speed0 = math.sqrt(boid.vx * boid.vx + boid.vy * boid.vy) + 1e-9
            hx, hy = boid.vx / speed0, boid.vy / speed0 #forward
            px, py = -hy, hx #left/right

            # Zero all accumulator variables
            xpos_avg = 0
            ypos_avg = 0
            xvel_avg = 0
            yvel_avg = 0
            neighboring_boids = 0
            close_dx = 0
            close_dy = 0

            weight_sum = 0.0
            front_pressure = 0.0
            back_pressure = 0.0
            turn_drive = 0.0

            # For every other boid in the flock
            for otherboid in self.boids:
                if boid is otherboid:
                    continue

                # Compute differences in x and y coordinates
                dx = boid.x - otherboid.x
                dy = boid.y - otherboid.y

                # Are both those differences less than the visual range?
                if abs(dx) < self.visual_range and abs(dy) < self.visual_range:
                    # Calculate the squared distance
                    squared_distance = dx * dx + dy * dy

                    # Is squared distance less than the protected range?
                    if squared_distance < self.protected_range_squared:
                        # Calculate difference in x/y-coordinates to nearfield boid
                        close_dx += boid.x - otherboid.x
                        close_dy += boid.y - otherboid.y

                    # Apply field of view + weights
                    elif squared_distance < self.visual_range_squared:
                        distance = math.sqrt(squared_distance) + 1e-9

                        # In which direction is the neighbor relative to me?
                        rx = -dx
                        ry = -dy
                        # Calculate cosine of the included angle
                        cosine = (rx * hx + ry * hy) / distance  # >0 ahead/<0 behind
                        if cosine < self.fieldofview:
                            continue

                        # Front-weighting-neighbors ahead influence more!
                        w = 1.0 + self.front_weight * max(0.0, cosine)
                        weight_sum += w

                        xpos_avg += w * otherboid.x
                        ypos_avg += w * otherboid.y
                        xvel_avg += w * otherboid.vx
                        yvel_avg += w * otherboid.vy

                        # Increment number of boids within visual range
                        neighboring_boids += 1

                        # Crowded ahead-slow down/crowded behind-speed up
                        front_pressure += max(0.0, cosine) / distance
                        back_pressure += max(0.0, -cosine) / distance

                        # Turning depends on left/right placement
                        leftright = (rx * px + ry * py) / distance
                        turn_drive += w * (leftright / distance)

            # If there were any boids in the visual range
            if neighboring_boids > 0 and weight_sum > 0:
                # Weighted averages instead of plain averages
                xpos_avg = xpos_avg / weight_sum
                ypos_avg = ypos_avg / weight_sum
                xvel_avg = xvel_avg / weight_sum
                yvel_avg = yvel_avg / weight_sum

                # Add the centering/matching contributions to velocity
                boid.vx = (boid.vx +
                           (xpos_avg - boid.x) * self.centering_factor +
                           (xvel_avg - boid.vx) * self.matching_factor)

                boid.vy = (boid.vy +
                           (ypos_avg - boid.y) * self.centering_factor +
                           (yvel_avg - boid.vy) * self.matching_factor)

            # Add the avoidance contribution to velocity
            boid.vx = boid.vx + (close_dx * self.avoid_factor)
            boid.vy = boid.vy + (close_dy * self.avoid_factor)
            
            # Predator avoidance
            for predator in self.predators:
                pred_dx = boid.x - predator.x
                pred_dy = boid.y - predator.y

                if math.sqrt(pred_dx * pred_dx + pred_dy * pred_dy) < self.predatory_range:
                    if pred_dx > 0:
                        boid.vx += self.predator_weight
                    if pred_dx < 0:
                        boid.vx -= self.predator_weight
                    if pred_dy > 0:
                        boid.vy += self.predator_weight
                    if pred_dy < 0:
                        boid.vy -= self.predator_weight

            # If the boid is near an edge, make it turn by turn_factor
            if boid.x < self.leftmargin:
                boid.vx = boid.vx + self.turn_factor
            if boid.x > self.rightmargin:
                boid.vx = boid.vx - self.turn_factor
            if boid.y > self.bottommargin:
                boid.vy = boid.vy - self.turn_factor
            if boid.y < self.topmargin:
                boid.vy = boid.vy + self.turn_factor

            # Rotate velocity slightly based on left/right drive
            dtheta = self.turning_control * turn_drive
            if dtheta > self.max_turn:
                dtheta = self.max_turn
            elif dtheta < -self.max_turn:
                dtheta = -self.max_turn

            cosd = math.cos(dtheta)
            sind = math.sin(dtheta)
            vx_new = boid.vx * cosd - boid.vy * sind
            vy_new = boid.vx * sind + boid.vy * cosd
            boid.vx, boid.vy = vx_new, vy_new

            # Speed up if crowded behind / slow down if crowded ahead
            speed_bias = self.speed_control * (back_pressure - front_pressure)
            speednow = math.sqrt(boid.vx * boid.vx + boid.vy * boid.vy) + 1e-9
            target_speed = speednow + speed_bias

            # Apply by scaling velocity-keeps direction
            if target_speed > 0:
                scale = target_speed / speednow
                boid.vx *= scale
                boid.vy *= scale
                speed = target_speed
            else:
                speed = speednow
                
            # Enforce min and max speeds
            if speed < self.minspeed:
                boid.vx = (boid.vx / speed) * self.minspeed
                boid.vy = (boid.vy / speed) * self.minspeed
            if speed > self.maxspeed:
                boid.vx = (boid.vx / speed) * self.maxspeed
                boid.vy = (boid.vy / speed) * self.maxspeed

            # Update boid's position
            boid.x += boid.vx
            boid.y += boid.vy

            # Hard wall constraint
            if boid.x < 0:
                boid.x = 0
                boid.vx = abs(boid.vx)
            elif boid.x > self.width:
                boid.x = self.width
                boid.vx = -abs(boid.vx)

            if boid.y < 0:
                boid.y = 0
                boid.vy = abs(boid.vy)
            elif boid.y > self.height:
                boid.y = self.height
                boid.vy = -abs(boid.vy)

        for predator in self.predators:
            for boid in self.boids:
                pred_dx = boid.x - predator.x
                pred_dy = boid.y - predator.y

                if math.sqrt(pred_dx * pred_dx + pred_dy * pred_dy) < self.predatory_range:
                    if pred_dx > 0:
                        predator.vx += self.predator_weight
                    if pred_dx < 0:
                        predator.vx -= self.predator_weight
                    if pred_dy > 0:
                        predator.vy += self.predator_weight
                    if pred_dy < 0:
                        predator.vy -= self.predator_weight

            # If the predator is near an edge, make it turn by turn_factor
            if predator.x < self.leftmargin:
                predator.vx += self.turn_factor_pred
            if predator.x > self.rightmargin:
                predator.vx -= self.turn_factor_pred
            if predator.y > self.bottommargin:
                predator.vy -= self.turn_factor_pred
            if predator.y < self.topmargin:
                predator.vy += self.turn_factor_pred

            # Enforce min and max speeds
            predator_speed = math.sqrt(predator.vx * predator.vx + predator.vy * predator.vy)
            if predator_speed < self.minspeed_pred:
                predator.vx = (predator.vx / predator_speed) * self.minspeed_pred
                predator.vy = (predator.vy / predator_speed) * self.minspeed_pred
            if predator_speed > self.maxspeed_pred:
                predator.vx = (predator.vx / predator_speed) * self.maxspeed_pred
                predator.vy = (predator.vy / predator_speed) * self.maxspeed_pred

            # Update predators's position
            predator.x += predator.vx
            predator.y += predator.vy

            # Hard wall constraint
            if predator.x < 0:
                predator.x = 0
                predator.vx = abs(predator.vx)
            elif predator.x > self.width:
                predator.x = self.width
                predator.vx = -abs(predator.vx)

            if predator.y < 0:
                predator.y = 0
                predator.vy = abs(predator.vy)
            elif predator.y > self.height:
                predator.y = self.height
                predator.vy = -abs(predator.vy)

    def get_states(self):
        """Return numpy arrays of boid positions and velocities."""
        count = len(self.boids)
        px = np.zeros(count, dtype=np.float64)
        py = np.zeros(count, dtype=np.float64)
        vx = np.zeros(count, dtype=np.float64)
        vy = np.zeros(count, dtype=np.float64)

        for i, boid in enumerate(self.boids):
            px[i] = boid.x
            py[i] = boid.y
            vx[i] = boid.vx
            vy[i] = boid.vy

        return px, py, vx, vy


class BoidsVisualizer:
    def __init__(self, num_boids=100, num_preds=1, width=640, height=480):
        self.sim = BoidsSimulation(num_boids, num_preds, width, height)

        # Create tkinter window
        self.root = tk.Tk()
        self.root.title("Boids Simulation")

        # Roughly 60 fps, but highly dependent on device and param configuration.
        self.delay = 16

        # Create canvas
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg='white')
        self.canvas.pack()

        # Toggle buttons for ui/settings and stat visualization.
        self.stats_open = False
        self.ui_open = False

        self.stat_button = tk.Button(self.root, text='Stats', command=self.toggle_stats, bg='#FF4646', activebackground='#D73535')
        self.ui_button = tk.Button(self.root, text='Settings', command=self.toggle_settings, bg='#FF4646', activebackground='#D73535')
        self.stat_button.pack(side=tk.LEFT)
        self.ui_button.pack(side=tk.LEFT)

        # Store triangle IDs for each boid
        self.triangles = []
        for _ in self.sim.boids:
            triangle = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill='blue', outline='darkblue')
            self.triangles.append(triangle)

        # Store triangle IDs for each predator
        self.triangles_pred = []
        for _ in self.sim.predators:
            triangle_pred = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill='red', outline='darkred')
            self.triangles_pred.append(triangle_pred)

        # Initialize frame counter and tunable x range for stats window.
        self.frame = 1

        # Tunable parameters
        self.triangle_size = 3
        self.stat_xrange = 2000  # For stat window only
        self.triangle_size = 3

        # Start animation
        self.animate()
        self.root.mainloop()

    def edit_boid_count(self):
        self.canvas.delete(0, tk.END)
        for triangle in self.triangles:
            self.canvas.delete(triangle)
        self.sim.edit_boid_count()
        self.triangles = []
        for _ in self.sim.boids:
            triangle = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill='blue', outline='darkblue')
            self.triangles.append(triangle)

    def get_triangle_points(self, boid):
        """Calculate triangle vertices based on boid position and velocity"""
        size = self.triangle_size
        # Calculate angle from velocity
        angle = math.atan2(boid.vy, boid.vx)

        # Triangle points (pointing in direction of travel)
        # Front point
        x1 = boid.x + size * math.cos(angle)
        y1 = boid.y + size * math.sin(angle)

        # Back left point
        x2 = boid.x + size * math.cos(angle + 2.5)
        y2 = boid.y + size * math.sin(angle + 2.5)

        # Back right point
        x3 = boid.x + size * math.cos(angle - 2.5)
        y3 = boid.y + size * math.sin(angle - 2.5)

        return [x1, y1, x2, y2, x3, y3]

    def animate(self):
        """Update animation frame"""
        self.sim.update()

        # Update each boid triangle
        for i, boid in enumerate(self.sim.boids):
            points = self.get_triangle_points(boid)
            self.canvas.coords(self.triangles[i], *points)
        
        # Update each predator triangle
        for j, predator in enumerate(self.sim.predators):
            points = self.get_triangle_points(predator)
            self.canvas.coords(self.triangles_pred[j], *points)

        if self.stats_open:
            self.stats.update()

        # Schedule next frame (approximately 60 FPS)
        self.frame += 1
        self.root.after(self.delay, self.animate)

    def resize(self):
        """Function in subclass updates width, height, and margin. This function resizes
        the canvas and computes new margin bounds."""
        self.sim.leftmargin = self.sim.margin
        self.sim.rightmargin = self.sim.width - self.sim.margin
        self.sim.topmargin = self.sim.margin
        self.sim.bottommargin = self.sim.height - self.sim.margin

        self.canvas.config(width=self.sim.width, height=self.sim.height)

    def toggle_stats(self):
        if self.stats_open:
            self.stats.close()
            self.stats = None
            self.stat_button.config(bg='#FF4646', activebackground='#D73535')

        else: 
            self.stats = StatWindow(self)
            self.stat_button.config(bg='#74c476', activebackground='#41ab5d')

        self.stats_open = not self.stats_open

    def toggle_settings(self):
        if self.ui_open:
            self.ui.close()
            self.ui = None
            self.ui_button.config(bg='#FF4646', activebackground='#D73535')

        else: 
            self.ui = SettingsWindow(self)
            self.ui_button.config(bg='#74c476', activebackground='#41ab5d')

        self.ui_open = not self.ui_open

SIM = None

def terminate(sig, _):
    """Needed for proper termination of program on ctrl+c / keyboard interrupt."""
    try:
        SIM.canvas.destroy()
    except:
        sys.exit(0)

if __name__ == "__main__":
    # Run the simulation with visualization
    signal.signal(signal.SIGINT, terminate)
    BoidsVisualizer(num_boids=100, num_preds=2, width=640, height=480)
    #BoidsVisualizer(num_boids=300, width=300, height=300)