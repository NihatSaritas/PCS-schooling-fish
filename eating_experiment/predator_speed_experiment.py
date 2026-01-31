"""
Eating experiment where predator movement and turning speed is scaled on x-axis. The
number of remaining fish after 2000 frames can be seen on the y-axis. Generates boxplot
with colorcoded eating duration of 30 and 60 frames to show how this moves the bottleneck.
"""

from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
from boids_hunteradams import BoidsSimulation
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EatingExperiment:
    """
    Runs eating experiments with various parameters and tracks eating behavior.
    """

    def __init__(self, duration_frames: int = 6000, repetitions: int = 10):
        """
        Initialize the eating experiment.

        Args:
            duration_frames: Number of frames to run each experiment (default: 6000, ~100 seconds
                             at 60fps)
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
        # eating_duration: int = 60,
        seed: int = None,
        width: int = 640,
        height: int = 480,
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
            num_boids=num_boids, num_preds=num_preds, width=width, height=height, seed=seed
        )

        # Modify the parameters (speed and turning factor)
        sim.maxspeed_pred = maxspeed_pred
        sim.minspeed_pred = minspeed_pred
        sim.turn_factor_pred = turn_factor_pred
        sim.eating_duration = self.eating_duration

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
            "params": {
                "num_boids": num_boids,
                "num_preds": num_preds,
                "maxspeed_pred": maxspeed_pred,
                "minspeed_pred": minspeed_pred,
                "turn_factor_pred": turn_factor_pred,
                "seed": seed,
            },
            "time_points": time_points,
            "fish_eaten": fish_eaten,
            "fish_remaining": fish_remaining,
            "initial_boids": initial_boids,
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
            print(f"Running experiment {i + 1}/{len(param_sets)}...")
            print(f"  Parameters: {params}")

            avg_fish_eaten = []
            avg_fish_remaining = []
            repetition = []
            for j in range(self.repetitions):
                result = self.run_experiment(**params)
                params["seed"] += "/" + str(54321 * j)

                avg_fish_eaten.append(result["fish_eaten"][-1])
                avg_fish_remaining.append(result["fish_remaining"][-1])
                repetition.append(j + 1)

            results.append(
                {
                    "params": params,
                    "repetition": repetition,
                    "last_time_point": result["time_points"][-1],
                    "average_fish_eaten": avg_fish_eaten,
                    "average_fish_remaining": avg_fish_remaining,
                    "initial_boids": result["initial_boids"],
                }
            )

            # Print summary
            final_eaten = avg_fish_eaten
            final_frame = result["time_points"][-1]
            print(
                f"  Result: {final_eaten}/{result['initial_boids']} fish eaten by frame "
                f"{final_frame}")
            print()

        if self.eating_duration == 60:
            self.results60 = results
        else:
            self.results30 = results
        return results

    def plot_results(self, save_path: str = None):
        """
        Plot eating behavior over time for all experiments.

        Args:
            save_path: Optional path to save the plot
        """
        if not self.results60 or not self.results30:
            print("No results to plot. Run experiments first.")
            return

        fig, ax = plt.subplots(1, 1, figsize=(12, 5))

        # Create 2 boxplots for predator speed (x-axis). Colorcoded facecolors and medians for
        # the 30 frame and 60 frame eating durations.
        for type in [30, 60]:
            if type == 60:
                results = self.results60
                facecolor = "mediumblue"
                mediancolor = "turquoise"
            else:
                results = self.results30
                facecolor = "red"
                mediancolor = "darkred"

            fish_remaining = []
            for result in results:
                fish_remaining.append(result["average_fish_remaining"])

            bp = ax.boxplot(
                fish_remaining,
                tick_labels=self.x,
                patch_artist=True,
                medianprops=dict(color=mediancolor, linewidth=1.5),
                label=f"{type} frame eating duration",
            )

            for patch in bp["boxes"]:
                patch.set_facecolor(facecolor)
                patch.set_alpha(0.6)

        ax.set_xlabel("Predator to fish mobility ratio (x fish baseline)", fontsize=12)
        ax.set_ylabel("Number of Fish Remaining", fontsize=12)
        ax.set_title(
            "Fish Remaining for various predator configurations", fontsize=14, fontweight="bold"
        )
        ax.legend(fontsize=9, loc="best")
        ax.grid(True, alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=60, ha="center", rotation_mode="anchor")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {save_path}")

        plt.show()


def example_experiments(repetitions):
    """
    Example: Run experiments with different matching_factor (alignment) values.
    All other parameters use defaults from boids_hunteradams.py.
    """
    # Initialize experiment
    experiment = EatingExperiment(duration_frames=2000, repetitions=repetitions)

    # Define parameter sets to test
    experiment_count = 45  # Makes jumps of 0.1
    minspeed_baseline, maxspeed_baseline, turn_factor_baseline = 6, 3, 0.2
    minfactor = 0.1  # start at 0.1 * speed_baseline
    maxfactor = 4.5  # end at 4.5 * speed_baseline

    minspeeds = np.linspace(
        minfactor * minspeed_baseline, maxfactor * maxspeed_baseline, experiment_count
    )
    maxspeeds = np.linspace(
        minfactor * maxspeed_baseline, maxfactor * maxspeed_baseline, experiment_count
    )
    turn_factors = np.linspace(
        minfactor * turn_factor_baseline, maxfactor * turn_factor_baseline, experiment_count
    )
    experiment.x = np.round(np.linspace(minfactor, maxfactor, experiment_count), 1)

    param_sets = [
        {
            "num_boids": 50,
            "num_preds": 1,
            "maxspeed_pred": maxspeeds[i],
            "minspeed_pred": minspeeds[i],
            "turn_factor_pred": turn_factors[i],
            "seed": str(12345 * i) + "/" + "5062PRCS6Y",
        }
        for i in range(experiment_count)
    ]

    # Run experiments
    experiment.eating_duration = 60
    experiment.run_multiple_experiments(param_sets)

    experiment.eating_duration = 30
    experiment.run_multiple_experiments(param_sets)

    # Plot results
    experiment.plot_results(save_path="speed_experiment_double.png")

    return experiment


if __name__ == "__main__":
    print("=" * 60)
    print("Fish Eating Experiment")
    print("=" * 60)
    print()

    # Run example experiments
    repetitions = 20
    experiment = example_experiments(repetitions)

    print("\nExperiment complete!")
