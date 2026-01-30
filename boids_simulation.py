"""Old prototype for boids simulator. Use boids_hunteradams.py for final version."""
import tkinter as tk
import math
import random


class Boid:
    """Represents a single fish/boid in the simulation."""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.width = width
        self.height = height
        
    def distance(self, other):
        """Calculate distance to another boid."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def update(self, boids, params):
        """Update boid position based on the three rules."""
        # Find neighbors within perception radius
        neighbors = [b for b in boids if b != self and self.distance(b) < params['perception_radius']]
        
        if neighbors:
            # Cohesion: move toward center of mass
            cohesion_x, cohesion_y = self.cohesion(neighbors)
            
            # Separation: avoid crowding
            separation_x, separation_y = self.separation(neighbors, params['min_distance'])
            
            # Alignment: match velocity
            alignment_x, alignment_y = self.alignment(neighbors)
            
            # Apply forces with weights
            self.vx += cohesion_x * params['cohesion_weight']
            self.vy += cohesion_y * params['cohesion_weight']
            
            self.vx += separation_x * params['separation_weight']
            self.vy += separation_y * params['separation_weight']
            
            self.vx += alignment_x * params['alignment_weight']
            self.vy += alignment_y * params['alignment_weight']
        
        # Wall avoidance
        wall_x, wall_y = self.avoid_walls(params['wall_margin'])
        self.vx += wall_x * params['wall_weight']
        self.vy += wall_y * params['wall_weight']
        
        # Limit speed
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > params['max_speed']:
            self.vx = (self.vx / speed) * params['max_speed']
            self.vy = (self.vy / speed) * params['max_speed']
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Keep fish within bounds (hard constraint)
        self.x = max(0, min(self.width, self.x))
        self.y = max(0, min(self.height, self.y))
    
    def cohesion(self, neighbors):
        """Move toward the average position of neighbors."""
        center_x = sum(b.x for b in neighbors) / len(neighbors)
        center_y = sum(b.y for b in neighbors) / len(neighbors)
        return (center_x - self.x) * 0.01, (center_y - self.y) * 0.01
    
    def separation(self, neighbors, min_distance):
        """Avoid getting too close to neighbors."""
        move_x = 0
        move_y = 0
        for other in neighbors:
            dist = self.distance(other)
            if dist < min_distance and dist > 0:
                move_x += (self.x - other.x) / dist
                move_y += (self.y - other.y) / dist
        return move_x, move_y
    
    def alignment(self, neighbors):
        """Match the average velocity of neighbors."""
        avg_vx = sum(b.vx for b in neighbors) / len(neighbors)
        avg_vy = sum(b.vy for b in neighbors) / len(neighbors)
        return (avg_vx - self.vx) * 0.05, (avg_vy - self.vy) * 0.05
    
    def avoid_walls(self, margin):
        """Avoid walls with repulsive force similar to separation."""
        move_x = 0
        move_y = 0
        
        # Left wall
        if self.x < margin:
            move_x += (margin - self.x) / margin
        # Right wall
        elif self.x > self.width - margin:
            move_x -= (self.x - (self.width - margin)) / margin
        
        # Top wall
        if self.y < margin:
            move_y += (margin - self.y) / margin
        # Bottom wall
        elif self.y > self.height - margin:
            move_y -= (self.y - (self.height - margin)) / margin
        
        return move_x, move_y


class BoidsSimulation:
    """Main simulation class with tkinter visualization."""
    
    def __init__(self, width=800, height=600, num_boids=50):
        self.width = width
        self.height = height
        self.num_boids = num_boids
        
        # Simulation parameters
        self.params = {
            'perception_radius': 75,
            'min_distance': 25,
            'max_speed': 4,
            'cohesion_weight': 1.0,
            'separation_weight': 1.5,
            'alignment_weight': 1.0,
            'wall_margin': 50,
            'wall_weight': 2.0
        }
        
        # Initialize boids
        self.boids = [Boid(
            random.uniform(0, width),
            random.uniform(0, height),
            width,
            height
        ) for _ in range(num_boids)]
        
        # Setup GUI
        self.root = tk.Tk()
        self.root.title("Boids Simulation - Fish Schooling")
        
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg='lightblue')
        self.canvas.pack()
        
        self.running = True
        self.animate()
    
    def draw_boid(self, boid):
        """Draw a boid as a triangle pointing in its direction of movement."""
        # Calculate heading angle
        angle = math.atan2(boid.vy, boid.vx)
        
        # Triangle size
        size = 8
        
        # Calculate triangle points
        point1_x = boid.x + size * math.cos(angle)
        point1_y = boid.y + size * math.sin(angle)
        
        point2_x = boid.x + size * math.cos(angle + 2.5)
        point2_y = boid.y + size * math.sin(angle + 2.5)
        
        point3_x = boid.x + size * math.cos(angle - 2.5)
        point3_y = boid.y + size * math.sin(angle - 2.5)
        
        # Draw triangle
        self.canvas.create_polygon(
            point1_x, point1_y,
            point2_x, point2_y,
            point3_x, point3_y,
            fill='darkblue',
            outline='blue'
        )
    
    def animate(self):
        """Main animation loop."""
        if self.running:
            # Update all boids
            for boid in self.boids:
                boid.update(self.boids, self.params)
            
            # Redraw
            self.canvas.delete('all')
            for boid in self.boids:
                self.draw_boid(boid)
            
            # Schedule next frame (approximately 60 FPS)
            self.root.after(16, self.animate)
    
    def run(self):
        """Start the simulation."""
        self.root.mainloop()


if __name__ == "__main__":
    simulation = BoidsSimulation(width=800, height=600, num_boids=50)
    simulation.run()
