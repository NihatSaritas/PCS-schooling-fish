"""
Experiment to track fish eating behavior over time with multiple parameters.

This module runs simulations with different parameter configurations and tracks
how many fish have been eaten by predators at different time points.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boids_hunteradams import BoidsSimulation
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple


class EatingExperiment:
    """
    Runs eating experiments with various parameters and tracks eating behavior.
    """
    
    def __init__(self, duration_frames: int = 6000, repetitions: int = 10):
        """
        Initialize the eating experiment.
        
        Args:
            duration_frames: Number of frames to run each experiment (default: 6000, ~100 seconds at 60fps)
        """
        self.duration_frames = duration_frames
        self.results = []
        self.repetitions = repetitions
        
    def run_experiment(
        self,
        num_boids: int = 50,
        num_preds: int = 1,
        maxspeed_pred: float = 3.3,
        minspeed_pred: float = 2.2,
        turn_factor_pred: float = 0.2,
        seed: int = None,
        width: int = 640,
        height: int = 480
    ) -> Dict:
        """
        Run a single experiment with specified parameters.
        Uses default parameters from boids_hunteradams.py except for matching_factor.
        
        Args:
            num_boids: Initial number of fish/boids
            num_preds: Number of predators
            matching_factor: Alignment/velocity matching factor (default: 0.05)
            seed: Random seed for reproducibility
            width: Simulation width
            height: Simulation height
            
        Returns:
            Dictionary containing experiment results
        """
        # Initialize simulation with default parameters
        sim = BoidsSimulation(
            num_boids=num_boids,
            num_preds=num_preds,
            width=width,
            height=height,
            seed=seed
        )
        
        # Modify the parameters (alignment parameter)
        sim.maxspeed_pred = maxspeed_pred
        sim.minspeed_pred = minspeed_pred
        sim.turn_factor_pred = turn_factor_pred
        
        # Track eating over time
        initial_boids = num_boids
        time_points = []
        fish_eaten = []
        fish_remaining = []
        
        # Run simulation
        for frame in range(self.duration_frames):
            sim.update()
            
            # Record data every 100 frames (~1.67 seconds at 60fps)
            if frame % 100 == 0:
                time_points.append(frame)
                eaten = initial_boids - sim.num_boids
                fish_eaten.append(eaten)
                fish_remaining.append(sim.num_boids)
                
            # Stop if all fish are eaten
            if sim.num_boids == 0:
                # Fill remaining time points with final values
                remaining_frames = range(frame, self.duration_frames, 100)
                for f in remaining_frames:
                    time_points.append(f)
                    fish_eaten.append(initial_boids)
                    fish_remaining.append(0)
                break
        
        # Store results
        result = {
            'params': {
                'num_boids': num_boids,
                'num_preds': num_preds,
                'maxspeed_pred': maxspeed_pred,
                'minspeed_pred': minspeed_pred,
                'turn_factor_pred': turn_factor_pred,
                'seed': seed
            },
            'time_points': time_points,
            'fish_eaten': fish_eaten,
            'fish_remaining': fish_remaining,
            'initial_boids': initial_boids
        }
        
        return result
    
    def run_multiple_experiments(self, param_sets: List[Dict]) -> List[Dict]:
        """
        Run multiple experiments with different parameter sets.
        
        Args:
            param_sets: List of parameter dictionaries to test
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        for i, params in enumerate(param_sets):
            print(f"Running experiment {i+1}/{len(param_sets)}...")
            print(f"  Parameters: {params}")

            avg_fish_eaten = []
            avg_fish_remaining = []
            repetition = []
            for j in range(self.repetitions):
                result = self.run_experiment(**params)
                params['seed'] += 1
            
                avg_fish_eaten.append(result['fish_eaten'][-1])
                avg_fish_remaining.append(result['fish_remaining'][-1])
                repetition.append(j+1)
            
            results.append({'params': params, 
                            'repetition': repetition,
                            'last_time_point': result['time_points'][-1],
                            'average_fish_eaten': avg_fish_eaten,
                            'average_fish_remaining': avg_fish_remaining,
                            'initial_boids': result['initial_boids']})
            
            # Print summary
            # final_eaten = result['fish_eaten'][-1]
            final_eaten = avg_fish_eaten
            final_frame = result['time_points'][-1]
            print(f"  Result: {final_eaten}/{result['initial_boids']} fish eaten by frame {final_frame}")
            print()
        
        self.results = results
        return results
    
    def plot_results(self, save_path: str = None):
        """
        Plot eating behavior over time for all experiments.
        
        Args:
            save_path: Optional path to save the plot
        """
        if not self.results:
            print("No results to plot. Run experiments first.")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Fish eaten over time
        fish_eaten = []
        changing_values = []
        for i, result in enumerate(self.results):

            # time_seconds = np.array(result['time_points']) / 60.0  # Convert frames to seconds
            params = result['params']
            changing_values.append([params[f'maxspeed_pred'], params[f'minspeed_pred'], params[f'turn_factor_pred']])
            fish_eaten.append(result['average_fish_eaten'])
        
        ax1.boxplot(fish_eaten, tick_labels=changing_values)

        # ax1.plot(time_seconds, result['fish_eaten'], marker='o', markersize=3, label=label)
        ax1.set_xlabel(f'Change in max- and minspeed and turnfactor', fontsize=12)
        ax1.set_ylabel('Number of Fish Eaten', fontsize=12)
        ax1.set_title('Fish Eaten Over Time', fontsize=14, fontweight='bold')
        # ax1.legend(fontsize=9, loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Fish remaining over time
        fish_remaining = []
        for i, result in enumerate(self.results):
            # time_seconds = np.array(result['time_points']) / 60.0
            params = result['params']
            fish_remaining.append(result['average_fish_remaining'])

        ax2.boxplot(fish_remaining, tick_labels=changing_values)
        # ax2.plot(time_seconds, result['fish_remaining'], marker='o', markersize=3, label=label)
    
        ax1.set_xlabel(f'Change in max- and minspeed and turnfactor', fontsize=12)
        ax2.set_ylabel('Number of Fish Remaining', fontsize=12)
        ax2.set_title('Fish Remaining Over Time', fontsize=14, fontweight='bold')
        # ax2.legend(fontsize=9, loc='best')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        plt.show()
    
    def save_results_to_csv(self, filepath: str):
        """
        Save experiment results to a CSV file.
        
        Args:
            filepath: Path to save the CSV file
        """
        if not self.results:
            print("No results to save. Run experiments first.")
            return
        
        import csv
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'experiment_id', 'repetition', 'num_boids', 'num_preds', 'maxspeed_pred', 'minspeed_pred', 'turn_factor_pred', 'seed',
                'fish_eaten', 'fish_remaining'
            ])
            
            # Write data
            for exp_id, result in enumerate(self.results):
                params = result['params']
                for repetition, eaten, remaining in zip(
                    result['repetition'],
                    result['average_fish_eaten'],
                    result['average_fish_remaining']
                ):
                    writer.writerow([
                        exp_id,
                        repetition,
                        params['num_boids'],
                        params['num_preds'],
                        params['maxspeed_pred'],
                        params['minspeed_pred'],
                        params['turn_factor_pred'],
                        params['seed'],
                        eaten,
                        remaining
                    ])
        
        print(f"Results saved to {filepath}")


def example_experiments(repetitions):
    """
    Example: Run experiments with different matching_factor (alignment) values.
    All other parameters use defaults from boids_hunteradams.py.
    """
    # Initialize experiment
    experiment = EatingExperiment(duration_frames=6000, repetitions=repetitions)
    
    # Define parameter sets to test
    param_sets = [
        # 50% lower than fish speed
        {
            'num_boids': 50,
            'num_preds': 1,
            'maxspeed_pred': 1.5,
            'minspeed_pred': 1.0,
            'turn_factor_pred': 0.1,
            'seed': 42
        },
        # 10% lower than fish speed
        {
            'num_boids': 50,
            'num_preds': 1,
            'maxspeed_pred': 2.7,
            'minspeed_pred': 1.8,
            'turn_factor_pred': 0.2,
            'seed': 42
        },
        # Same speed as fish
        {
            'num_boids': 50,
            'num_preds': 1,
            'maxspeed_pred': 3.0,
            'minspeed_pred': 2.0,
            'turn_factor_pred': 0.2,
            'seed': 42
        },
        # Default parameters (10% higher than fish speed) (from boids_hunteradams.py)
        {
            'num_boids': 50,
            'num_preds': 1,
            'maxspeed_pred': 3.3,
            'minspeed_pred': 2.2,
            'turn_factor_pred': 0.2,
            'seed': 42
        },
        # 50% higher than fish speed TODO: find good turn factor
        {
            'num_boids': 50,
            'num_preds': 1,
            'maxspeed_pred': 4.5,
            'minspeed_pred': 3.0,
            'turn_factor_pred': 0.3,
            'seed': 42
        },
        # 100% higher than fish speed
        {
            'num_boids': 50,
            'num_preds': 1,
            'maxspeed_pred': 6,
            'minspeed_pred': 4,
            'turn_factor_pred': 0.4,
            'seed': 42
        }
    ]
    
    # Run experiments
    results = experiment.run_multiple_experiments(param_sets)
    
    # Save results
    experiment.save_results_to_csv('speed_experiment_results.csv')
    
    # Plot results
    experiment.plot_results(save_path='speed_experiment_plot.png')
    
    return experiment


if __name__ == '__main__':
    print("=" * 60)
    print("Fish Eating Experiment")
    print("=" * 60)
    print()
    
    # Run example experiments
    repetitions = 10
    experiment = example_experiments(repetitions)
    
    print("\nExperiment complete!")
