import math
import random
import tkinter as tk

class Boid:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

class BoidsSimulation:
    def __init__(self, num_boids=50, width=640, height=480):
        # Tunable parameters
        self.turnfactor = 0.2
        self.visual_range = 40
        self.protected_range = 8
        self.centering_factor = 0.0005
        self.avoidfactor = 0.07
        self.matching_factor = 0.05
        self.maxspeed = 3
        self.minspeed = 2

        """Inspired additions by Katz-et-all"""
        self.fieldofview = math.cos(math.radians(170))  # small blind zone behind
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

    def update(self):
        """Update all boids for one timestep"""
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
            boid.vx = boid.vx + (close_dx * self.avoidfactor)
            boid.vy = boid.vy + (close_dy * self.avoidfactor)

            # If the boid is near an edge, make it turn by turnfactor
            if boid.x < self.leftmargin:
                boid.vx = boid.vx + self.turnfactor
            if boid.x > self.rightmargin:
                boid.vx = boid.vx - self.turnfactor
            if boid.y > self.bottommargin:
                boid.vy = boid.vy - self.turnfactor
            if boid.y < self.topmargin:
                boid.vy = boid.vy + self.turnfactor

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
            boid.x = boid.x + boid.vx
            boid.y = boid.y + boid.vy

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


class BoidsVisualizer:
    def __init__(self, num_boids=100, width=640, height=480):
        self.sim = BoidsSimulation(num_boids, width, height)

        # Create tkinter window
        self.root = tk.Tk()
        self.root.title("Boids Simulation")

        # Create canvas
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg='white')
        self.canvas.pack()

        # Store triangle IDs for each boid
        self.triangles = []
        for _ in self.sim.boids:
            triangle = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill='blue', outline='darkblue')
            self.triangles.append(triangle)

        # Start animation
        self.animate()
        self.root.mainloop()

    def get_triangle_points(self, boid, size=3):
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
        """Update animation frame"""
        # Update simulation
        self.sim.update()

        # Update each triangle
        for i, boid in enumerate(self.sim.boids):
            points = self.get_triangle_points(boid)
            self.canvas.coords(self.triangles[i], *points)

        # Schedule next frame (approximately 60 FPS)
        self.root.after(16, self.animate)


if __name__ == "__main__":
    # Run the simulation with visualization
    BoidsVisualizer(num_boids=100, width=640, height=480)