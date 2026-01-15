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
        self.avoidfactor = 0.05
        self.matching_factor = 0.05
        self.maxspeed = 3
        self.minspeed = 2
        
        # Screen dimensions
        self.width = width
        self.height = height
        
        # Margins for turning
        self.margin = 100
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
            # Zero all accumulator variables
            xpos_avg = 0
            ypos_avg = 0
            xvel_avg = 0
            yvel_avg = 0
            neighboring_boids = 0
            close_dx = 0
            close_dy = 0
            
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
                    
                    # If not in protected range, is the boid in the visual range?
                    elif squared_distance < self.visual_range_squared:
                        # Add other boid's x/y-coord and x/y vel to accumulator variables
                        xpos_avg += otherboid.x
                        ypos_avg += otherboid.y
                        xvel_avg += otherboid.vx
                        yvel_avg += otherboid.vy
                        
                        # Increment number of boids within visual range
                        neighboring_boids += 1
            
            # If there were any boids in the visual range
            if neighboring_boids > 0:
                # Divide accumulator variables by number of boids in visual range
                xpos_avg = xpos_avg / neighboring_boids
                ypos_avg = ypos_avg / neighboring_boids
                xvel_avg = xvel_avg / neighboring_boids
                yvel_avg = yvel_avg / neighboring_boids
                
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
            
            # Calculate the boid's speed
            speed = math.sqrt(boid.vx * boid.vx + boid.vy * boid.vy)
            
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
    
    def get_triangle_points(self, boid, size=5):
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
