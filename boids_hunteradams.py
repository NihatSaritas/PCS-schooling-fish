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
        self.is_eating = False
        self.eating_timer = 0

class BoidsSimulation:
    """Class containing the core components needed to run the boid simulation."""
    def __init__(self, num_boids=50, num_preds=1, width=640, height=480, seed=None):
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

        if seed:
            random.seed(seed)

        # Predator parameters
        self.num_preds = num_preds
        self.turn_factor_pred = 0.2
        self.visual_range_pred = 160
        self.predatory_range = 100
        self.eating_range = 20
        self.eating_duration = 60  # frames (~1 second at 60 FPS)
        self.pred2fish_attraction = 0.1
        self.fish2pred_avoidance = 0.15
        self.avoid_factor_pred = 0.1
        self.maxspeed_pred = 3.3
        self.minspeed_pred = 2.2

        # Additions inspired by Katz-et-all
        self.fieldofview_degrees = 340 # small blind zone behind
        self.fieldofview = math.cos(math.radians(self.fieldofview_degrees/2))
        self.front_weight = 0.3
        self.speed_control = 0.03
        self.turning_control = 0.05
        self.max_turn = 0.15

        # Shared parameters between fish and predator
        self.random_factor = 0.25
        self.random_freq = 0.15

        # Screen dimensions
        self.width = width
        self.height = height

        # Margins for turning (i.e. distance at which agents see the wall)
        self.margin = int(max(0.2 * width, 0.2 * height))
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
        for _ in range(self.num_preds):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            vx = random.uniform(-self.maxspeed_pred, self.maxspeed_pred)
            vy = random.uniform(-self.maxspeed_pred, self.maxspeed_pred)
            self.predators.append(Predator(x, y, vx, vy))

    def edit_boid_count(self):
        """Removes or adds boids until number of boids match the parameter. Editing
        the value of num_boids is handled by the user-interface. Removal is deterministic 
        and depends on the ordering in self.boids. Additions are psueodo-random, i.e. only 
        deterministic if a seed has been set."""
        while(len(self.boids) < self.num_boids):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            vx = random.uniform(-self.maxspeed, self.maxspeed)
            vy = random.uniform(-self.maxspeed, self.maxspeed)
            self.boids.append(Boid(x, y, vx, vy))

        if len(self.boids) > self.num_boids:      
            self.boids = self.boids[0:self.num_boids]

    def edit_pred_count(self):
        """Removes or adds predators until number of boids match the parameter. Editing
        the value of num_preds is handled by the user-interface. Removal is deterministic 
        and depends on the ordering in self.predators. Additions are psueodo-random, i.e.
        only deterministic if a seed has been set."""        
        while(len(self.predators) < self.num_preds):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            vx = random.uniform(-self.maxspeed_pred, self.maxspeed_pred)
            vy = random.uniform(-self.maxspeed_pred, self.maxspeed_pred)
            self.predators.append(Predator(x, y, vx, vy))

        if len(self.predators) > self.num_preds:      
            self.predators = self.predators[0:self.num_preds]

    def update_internal_vars(self):
        """ The user-interface may edit variables such as visual range, protected range, and field of 
        view. These parameters have corresponding precomputed values used by the simulation. This 
        function serves to update these precomputed internal variables."""
        self.fieldofview = math.cos(math.radians(self.fieldofview_degrees/2))
        self.visual_range_squared = self.visual_range ** 2
        self.protected_range_squared = self.protected_range ** 2

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
                        boid.vx += self.fish2pred_avoidance
                    if pred_dx < 0:
                        boid.vx -= self.fish2pred_avoidance
                    if pred_dy > 0:
                        boid.vy += self.fish2pred_avoidance
                    if pred_dy < 0:
                        boid.vy -= self.fish2pred_avoidance

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

            # Add random noise to turn if applicable.
            random_event = random.uniform(0,1)
            if random_event < self.random_freq:
                # Reduce randomness in large schools.
                strength = 1/neighboring_boids if neighboring_boids else 1
                noise = strength * random.uniform(-self.random_factor, self.random_factor)
                dtheta += noise

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

        self.boid_index = set()
        for predator in self.predators:
            # Handle eating state
            if predator.is_eating:
                predator.eating_timer -= 1
                if predator.eating_timer <= 0:
                    predator.is_eating = False
                else:
                    # Stay completely stationary while eating
                    continue
            
            boid_eaten = False
            fish_in_range = False
            i = 0
            for boid in self.boids:
                pred_dx = boid.x - predator.x
                pred_dy = boid.y - predator.y
                distance = math.sqrt(pred_dx * pred_dx + pred_dy * pred_dy)

                # Chasing after boid
                if distance < self.visual_range_pred:
                    fish_in_range = True
                    if pred_dx > 0:
                        predator.vx += self.pred2fish_attraction
                    if pred_dx < 0:
                        predator.vx -= self.pred2fish_attraction
                    if pred_dy > 0:
                        predator.vy += self.pred2fish_attraction
                    if pred_dy < 0:
                        predator.vy -= self.pred2fish_attraction

                    # A predator can eat one boid per frame if it's in eating range
                    if distance < self.eating_range and not boid_eaten:
                        boid_eaten = True
                        self.boid_index.add(i)
                        self.num_boids -= 1
                        # Start eating state - predator stops
                        predator.is_eating = True
                        predator.eating_timer = self.eating_duration
                        # Break out to skip rest of movement logic this frame
                        break

                i += 1
            
            # If predator just started eating, skip rest of movement logic
            if predator.is_eating:
                continue

            # Add random noise (roaming behavior) if predator is not actively chasing
            if not fish_in_range:
                noise = random.uniform(-self.random_factor, self.random_factor)
                vx, vy = predator.vx, predator.vy
                cosr = math.cos(noise)
                sinr = math.sin(noise)

                predator.vx = vx*cosr + vy*-sinr
                predator.vy = vx*sinr + vy*cosr

            # If the predator is near an edge, make it turn by turn_factor
            if predator.x < self.leftmargin:
                predator.vx += self.turn_factor_pred
            if predator.x > self.rightmargin:
                predator.vx -= self.turn_factor_pred
            if predator.y > self.bottommargin:
                predator.vy -= self.turn_factor_pred
            if predator.y < self.topmargin:
                predator.vy += self.turn_factor_pred

            # Avoid overlapping between sharks
            if self.num_preds > 1:
                for otherpredator in self.predators:
                    if predator is otherpredator:
                        continue
                    
                    dx = predator.x - otherpredator.x
                    dy = predator.y - otherpredator.y

                    if math.sqrt(dx * dx + dy * dy) < self.visual_range_pred:
                        if dx > 0:
                            predator.vx += self.avoid_factor_pred
                        if dx < 0:
                            predator.vx -= self.avoid_factor_pred
                        if dy > 0:
                            predator.vy += self.avoid_factor_pred
                        if dy < 0:
                            predator.vy -= self.avoid_factor_pred

            # Enforce min and max speeds
            predator_speed = math.sqrt(predator.vx * predator.vx + predator.vy * predator.vy)
            if predator_speed > 0:  # Avoid division by zero
                if predator_speed < self.minspeed_pred:
                    predator.vx = (predator.vx / predator_speed) * self.minspeed_pred
                    predator.vy = (predator.vy / predator_speed) * self.minspeed_pred
                if predator_speed > self.maxspeed_pred:
                    predator.vx = (predator.vx / predator_speed) * self.maxspeed_pred
                    predator.vy = (predator.vy / predator_speed) * self.maxspeed_pred
            else:
                # If predator has no velocity (shouldn't happen outside eating), give it random direction
                angle = random.uniform(0, 2 * math.pi)
                predator.vx = self.minspeed_pred * math.cos(angle)
                predator.vy = self.minspeed_pred * math.sin(angle)

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

        # Remove eaten boids
        self.boid_index = sorted(self.boid_index, reverse=True)

        for idx in self.boid_index:
            del self.boids[idx]

    def get_state_arrays(self):
        """Return numpy arrays of boid positions and velocities."""
        count = len(self.boids)

        if count == 0:
            return None

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
    
    def get_stats(self):
        """Compute and return the polarization and millin-index for the current boid positions.
        Used by the stats window to get behavioral metrics. For definitions, refer to the report."""
        res = self.get_state_arrays()
        if not res:
            return 1,0
        px, py, vx, vy = res

        # Compute the polarization.
        d = np.column_stack([vx, vy])
        lengths = np.linalg.norm(d, axis=1, keepdims=True)
        dnorm = d / lengths
        polarization = np.linalg.norm(np.mean(dnorm, axis=0))

        # Compute the milling index.
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


class BoidsVisualizer:
    """Visualization tool for the boid simulation. If the settings and/or stats window are toggled on, 
    the 2 files in '/boid_simulation_subclasses' are called to handle these."""
    def __init__(self, num_boids=100, num_preds=1, width=640, height=480, seed=None, pause_after=-1):
        # Tunable parameters
        self.triangle_size = 3 
        self.pred_triangle_size = 5
        self.stat_xrange = 2000

        # Initialize te simulation
        self.sim = BoidsSimulation(num_boids, num_preds, width, height, seed)
        self.pause_after = pause_after

        # Create tkinter window
        self.root = tk.Tk()
        self.root.title("Boids Simulation")

        # Roughly 60 fps, but highly dependent on device and param configuration
        self.delay = 16

        # Initialize frame counter
        self.frame = 1

        # Create canvas
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg='white')
        self.canvas.pack()

        # Create 2 information fields for number of boids and the current frame
        self.label_num_boids = tk.Label(
                self.root,
                text=f"Number of boids: {self.sim.num_boids}",
                fg="darkblue")
        self.label_num_boids.pack(side=tk.TOP, anchor='w')

        self.label_num_frame = tk.Label(
            self.root,
            text=f"Frame number: {self.frame}",
            fg="darkblue")
        self.label_num_frame.pack(side=tk.TOP, anchor='w')

        # Toggle buttons for ui/settings and stat visualization
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

        # Start animation
        self.animate()
        self.root.mainloop()

    def edit_boid_count(self):
        """Deletes current triangle objects on the canvas, calls the boids simulation class to update
        its list of boids to match the value of its internal parameter, then recreates triange objects
        for the changed list of boids. Editing the internal parameter is handled by the user-interface."""
        # Delete triangle objects for boids
        for triangle in self.triangles:
            self.canvas.delete(triangle)

        # Call simulation to update its list of boids
        self.sim.edit_boid_count()
        self.triangles = []

        # Redraw the triangle objects
        for _ in self.sim.boids:
            triangle = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill='blue', outline='darkblue')
            self.triangles.append(triangle)

    def edit_pred_count(self):
        """Deletes current triangle objects on the canvas for predators, calls the boids simulation class 
        to update its list of predators to match the value of its internal parameter, then recreates triange 
        objects for the changed list of predators. Editing the internal parameter is handled by the user-interface."""
        # Delete triangle objects for predators
        for triangle in self.triangles_pred:
            self.canvas.delete(triangle)

        # Call simulation to update its list of predators
        self.sim.edit_pred_count()

        # Redraw the triangle objects
        self.triangles_pred = []
        for _ in self.sim.predators:
            triangle = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill='red', outline='darkred')
            self.triangles_pred.append(triangle)

    def get_triangle_points(self, boid, size):
        """Calculate triangle vertices based on boid position and velocity"""
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
        """Update the animation by 1 frame."""
        if self.pause_after != -1:  # -1 corresponds to run indefenitelty setting
            if self.pause_after == 0:
                self.root.quit()
            else:
                self.pause_after -= 1

        # Run simulation for 1 timestep, then update the frame and boid counters
        self.sim.update()
        self.label_num_boids.config(text=f"Number of boids: {self.sim.num_boids}")
        self.label_num_frame.config(text=f"Frame number: {self.frame}")

        # Remove eaten boids from the canvas
        if len(self.sim.boid_index) > 0:
            for idx in self.sim.boid_index:
                self.canvas.delete(self.triangles[idx])
                del self.triangles[idx]

        # Update each boid triangle
        for i, boid in enumerate(self.sim.boids):
            points = self.get_triangle_points(boid, self.triangle_size)
            self.canvas.coords(self.triangles[i], *points)
        
        # Update each predator triangle
        for j, predator in enumerate(self.sim.predators):
            points = self.get_triangle_points(predator, self.pred_triangle_size)
            self.canvas.coords(self.triangles_pred[j], *points)

        # If toggled on, update the stats window by 1 timeframe
        if self.stats_open:
            self.stats.update()

        # Schedu(le next frame (default delay approximates 60 FPS, but this varies based on device)
        self.frame += 1
        self.root.after(self.delay, self.animate)

    def resume(self, pause_after=-1):
        """Run the simulation and animation for the specified number of frames. If no number is specified, 
        this will run indefenitely until the program is exited."""
        self.pause_after = pause_after
        self.root.mainloop()

    def resize(self):
        """This function resizes the canvas and computes new margin bounds. Updating the internal values
        of the width, height, and margin is handled by the user-interface."""
        self.sim.leftmargin = self.sim.margin
        self.sim.rightmargin = self.sim.width - self.sim.margin
        self.sim.topmargin = self.sim.margin
        self.sim.bottommargin = self.sim.height - self.sim.margin

        self.canvas.config(width=self.sim.width, height=self.sim.height)

    def toggle_stats(self):
        """Enable or disable the stats window depending on its current state."""
        if self.stats_open:
            self.stats.close()
            self.stats = None
            self.stat_button.config(bg='#FF4646', activebackground='#D73535')

        else: 
            self.stats = StatWindow(self)
            self.stat_button.config(bg='#74c476', activebackground='#41ab5d')

        self.stats_open = not self.stats_open

    def toggle_settings(self):
        """Enable or disable the settings window depending on its current state."""
        if self.ui_open:
            self.ui.close()
            self.ui = None
            self.ui_button.config(bg='#FF4646', activebackground='#D73535')

        else: 
            self.ui = SettingsWindow(self)
            self.ui_button.config(bg='#74c476', activebackground='#41ab5d')

        self.ui_open = not self.ui_open

    def close(self):
        """End the simulation and destroy the canvas. If this is called with a pending animation,
        it may print warnings on the console. This does lead to any unintended behavior and can
        safely be ignored."""
        self.sim = None
        self.root.destroy()
        self.root = None


def terminate(sig, _):
    """Needed for proper termination of program on ctrl+c / keyboard interrupt when multiple
    windows are open (like settings and/or stats)."""
    sys.exit(0)


if __name__ == "__main__":
    # Run the simulation with visualization
    signal.signal(signal.SIGINT, terminate)
    SIM = BoidsVisualizer(num_boids=50, num_preds=1, width=640, height=480, seed=None)
    #BoidsVisualizer(num_boids=300, width=300, height=300)
