"""
Experiment to track fish eating behavior over time with multiple parameters.

This module runs simulations with different parameter configurations and tracks
how many fish have been eaten by predators at different time points.
"""

from typing import Dict, List
import matplotlib.pyplot as plt
from boids_hunteradams import BoidsSimulation
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EatingExperiment:
    """
    Runs eating experiments with various parameters and tracks eating behavior.
    """

    def __init__(
        self, duration_frames: int = 6000, repetitions: int = 10, parameter_name: str = "matching"
    ):
        """
        Initialize the eating experiment.

        Args:
            duration_frames: Number of frames to run each experiment (default: 6000, ~100 seconds
                             at 60fps)
            repetitions: Number of times to repeat each parameter configuration
            parameter_name: Which parameter to vary ('matching', 'avoid', 'centering')
        """
        self.duration_frames = duration_frames
        self.results = []
        self.repetitions = repetitions
        self.parameter_name = parameter_name

    def run_experiment(
        self,
        num_boids: int = 50,
        num_preds: int = 1,
        matching_factor: float = 0.05,
        avoid_factor: float = 0.07,
        centering_factor: float = 0.0005,
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

        # Only modify the matching_factor (alignment parameter)
        sim.matching_factor = matching_factor
        sim.avoid_factor = avoid_factor
        sim.centering_factor = centering_factor

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
                "matching_factor": matching_factor,
                "avoid_factor": avoid_factor,
                "centering_factor": centering_factor,
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
            # Store all time series data for each repetition
            all_time_series = []

            for j in range(self.repetitions):
                # Use different seed for each repetition without mutating original params
                run_params = params.copy()
                run_params["seed"] = params["seed"] + j
                result = self.run_experiment(**run_params)

                avg_fish_eaten.append(result["fish_eaten"][-1])
                avg_fish_remaining.append(result["fish_remaining"][-1])
                repetition.append(j + 1)
                all_time_series.append(result)

            results.append(
                {
                    "params": params,
                    "repetition": repetition,
                    "last_time_point": result["time_points"][-1],
                    "average_fish_eaten": avg_fish_eaten,
                    "average_fish_remaining": avg_fish_remaining,
                    "initial_boids": result["initial_boids"],
                    "all_time_series": all_time_series,
                }
            )

            # Print summary
            # final_eaten = result['fish_eaten'][-1]
            final_eaten = avg_fish_eaten
            final_frame = result["time_points"][-1]
            print(
                f"  Result: {final_eaten}/{result['initial_boids']} fish eaten by frame "
                f"{final_frame}")
            print()

        self.results = results
        return results

    def plot_results(self, save_path: str = None):
        """
        Plot eating behavior as boxplots for all experiments.
        Creates boxplots showing fish remaining at the final timestep for each parameter value.

        Args:
            save_path: Optional path to save the plot
        """
        if not self.results:
            print("No results to plot. Run experiments first.")
            return

        # Get parameter name for labels
        param_key = f"{self.parameter_name}_factor"
        param_labels = {"matching": "Alignment", "avoid": "Separation", "centering": "Cohesion"}
        param_display = param_labels.get(self.parameter_name, self.parameter_name.capitalize())

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        # Collect data for boxplot
        fish_remaining_pct = []
        param_values = []

        for result in self.results:
            params = result["params"]
            param_value = params[param_key]
            param_values.append(f"{param_value:.4f}")

            # Calculate percentage of fish remaining for each repetition
            initial = result["initial_boids"]
            pct_remaining = [
                (remaining / initial) * 100 for remaining in result["average_fish_remaining"]
            ]
            fish_remaining_pct.append(pct_remaining)

        # Plot boxplot
        ax.boxplot(fish_remaining_pct, labels=param_values)
        ax.set_xlabel(f"{param_display} Factor", fontsize=12)
        ax.set_ylabel("Fish Remaining (%)", fontsize=12)
        ax.set_title(
            f"Percentage of Fish Remaining - Varying {param_display}",
            fontsize=14,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3, axis="y")
        ax.set_ylim(0, 100)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
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

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(
                [
                    "experiment_id",
                    "repetition",
                    "num_boids",
                    "num_preds",
                    "matching_factor",
                    "avoid_factor",
                    "centering_factor",
                    "seed",
                    "fish_eaten",
                    "fish_remaining",
                ]
            )

            # Write data
            for exp_id, result in enumerate(self.results):
                params = result["params"]
                for repetition, eaten, remaining in zip(
                    result["repetition"],
                    result["average_fish_eaten"],
                    result["average_fish_remaining"],
                ):
                    writer.writerow(
                        [
                            exp_id,
                            repetition,
                            params["num_boids"],
                            params["num_preds"],
                            params["matching_factor"],
                            params["avoid_factor"],
                            params["centering_factor"],
                            params["seed"],
                            eaten,
                            remaining,
                        ]
                    )

        print(f"Results saved to {filepath}")


def example_experiments(parameter_name: str = "matching", repetitions: int = 10):
    """
    Example: Run experiments varying one parameter while keeping others at defaults.

    Args:
        parameter_name: Which parameter to vary ('matching', 'avoid', 'centering')
        repetitions: Number of repetitions per parameter value

    All other parameters use defaults from boids_hunteradams.py:
    - matching_factor (alignment): 0.05
    - avoid_factor (separation): 0.07
    - centering_factor (cohesion): 0.0005
    """
    # Initialize experiment
    # 10000 frames (~167 seconds at 60fps)
    experiment = EatingExperiment(
        duration_frames=10000, repetitions=repetitions, parameter_name=parameter_name
    )

    # Define parameter sets to test - only varying matching_factor
    param_sets_alignment = [
        # Very low alignment (nearly independent movement)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.01,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Low alignment
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.03,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Default alignment (from boids_hunteradams.py)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Higher alignment
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.10,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Very high alignment (strong schooling)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.20,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.30,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.40,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.50,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.60,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
    ]

    param_sets_separation = [
        # Very low alignment (nearly independent movement)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.01,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Low alignment
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.03,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Default alignment (from boids_hunteradams.py)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Higher alignment
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.10,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Very high alignment (strong schooling)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.20,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.30,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.40,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.50,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.60,
            "centering_factor": 0.0005,
            "seed": 42,
        },
    ]

    param_sets_cohesion = [
        # Very low alignment (nearly independent movement)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0001,
            "seed": 42,
        },
        # Low alignment
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0003,
            "seed": 42,
        },
        # Default alignment (from boids_hunteradams.py)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0005,
            "seed": 42,
        },
        # Higher alignment
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0010,
            "seed": 42,
        },
        # Very high alignment (strong schooling)
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0020,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0030,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0040,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0050,
            "seed": 42,
        },
        {
            "num_boids": 100,
            "num_preds": 1,
            "matching_factor": 0.05,
            "avoid_factor": 0.07,
            "centering_factor": 0.0060,
            "seed": 42,
        },
    ]

    # Run experiments
    if experiment.parameter_name == "matching":
        _ = experiment.run_multiple_experiments(param_sets_alignment)
    elif experiment.parameter_name == "avoid":
        _ = experiment.run_multiple_experiments(param_sets_separation)
    elif experiment.parameter_name == "centering":
        _ = experiment.run_multiple_experiments(param_sets_cohesion)

    # Save results
    experiment.save_results_to_csv(f"{experiment.parameter_name}_eating_experiment_results.csv")

    # Plot results
    experiment.plot_results(save_path=f"{experiment.parameter_name}_eating_experiment_plot.png")

    return experiment


if __name__ == "__main__":
    print("=" * 60)
    print("Fish Eating Experiment")
    print("=" * 60)
    print()

    # Run example experiments
    # Choose which parameter to vary: 'matching' (alignment) / 'avoid'
    # (separation) / 'centering' (cohesion)
    parameter_to_vary = "matching"
    repetitions = 20
    experiment = example_experiments(parameter_name=parameter_to_vary, repetitions=repetitions)

    print("\nExperiment complete!")
