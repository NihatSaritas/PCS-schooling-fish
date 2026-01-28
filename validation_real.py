import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ks_2samp
from boids_hunteradams import BoidsSimulation

import random, numpy as np
random.seed(1000)
np.random.seed(1000)


def metrics(px_raw, py_raw, vx_raw, vy_raw):
    """Clean raw per-frame arrays and compute"""
    px = np.array(px_raw, dtype=float)
    py = np.array(py_raw, dtype=float)
    vx = np.array(vx_raw, dtype=float)
    vy = np.array(vy_raw, dtype=float)
    mask = ~np.isnan(px) & ~np.isnan(py) & ~np.isnan(vx) & ~np.isnan(vy)
    px, py, vx, vy = px[mask], py[mask], vx[mask], vy[mask]#No None
    
    if len(px) < 2: 
        return None, None, None

    # Polarization-same as we did in the model
    speeds = np.sqrt(vx**2 + vy**2) + 1e-9
    ux, uy = vx/speeds, vy/speeds
    pol = np.sqrt(np.mean(ux)**2 + np.mean(uy)**2)

    # Nearest-neighbor distance 
    dx = px[:, None] - px[None, :]
    dy = py[:, None] - py[None, :]
    dist2 = dx**2 + dy**2
    np.fill_diagonal(dist2, np.inf)
    nnds = np.sqrt(np.min(dist2, axis=1))
    
    return pol, nnds, (px, py, vx, vy)

def anisotropy(px, py, vx, vy, limit=150):
    """Build a neighbor density map in body-centered coordinates"""
    relative_coords = []
    for i in range(len(px)):
        dx = px - px[i]
        dy = py - py[i]
        
        # Define local coordinate frame from i's velocity direction
        speed = np.sqrt(vx[i]**2 + vy[i]**2) + 1e-9
        hx, hy = vx[i] / speed, vy[i] / speed #forward
        px_u, py_u = -hy, hx #lateral

        # Project
        rx = dx * px_u + dy * py_u 
        ry = dx * hx + dy * hy 
        
        # Keep neighbors in limit radius
        mask = (rx**2 + ry**2 < limit**2) & (rx**2 + ry**2 > 0)
        relative_coords.extend(zip(rx[mask], ry[mask]))
    return relative_coords


def experiment(data_path, sim_config):
    with open(data_path, 'r') as f:
        real_raw = json.load(f)
    
    real_pols, real_nnds, real_rel = [], [], []
    for k in list(real_raw.keys())[::20]: #sample
        f = real_raw[k]
        p, n, clean_data = metrics(np.array(f['px']), np.array(f['py']), 
                                       np.array(f['vx']), np.array(f['vy']))
        real_pols.append(p)
        real_nnds.extend(n)
        real_rel.extend(anisotropy(*clean_data))

    # Boids simulation
    sim = BoidsSimulation(**sim_config)
    # Put ideal parameters
    sim.visual_range = 70
    sim.matching_factor = 0.05
    sim.protected_range = 25

    # Update squared thresholds
    sim.visual_range_squared = sim.visual_range * sim.visual_range
    sim.protected_range_squared = sim.protected_range * sim.protected_range
    
    sim_pols, sim_nnds, sim_rel = [], [], []
    for i in range(5000): 
        sim.update()
        if i > 300: #not beginning
            px = np.array([b.x for b in sim.boids])
            py = np.array([b.y for b in sim.boids])
            vx = np.array([b.vx for b in sim.boids])
            vy = np.array([b.vy for b in sim.boids])
            p, n, clean_data = metrics(px, py, vx, vy)
            sim_pols.append(p)
            sim_nnds.extend(n)
            if i % 10 == 0:
                sim_rel.extend(anisotropy(*clean_data))

    return (real_pols, real_nnds, real_rel), (sim_pols, sim_nnds, sim_rel)

# Visualization
def plot_science_report(real, sim):
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    sns.set_context("paper", font_scale=1.5)

    # Polarization 
    axes[0].boxplot([real[0], sim[0]], tick_labels=['Dataset', 'Boids'], patch_artist=True)
    axes[0].set_title("A. Polarization ")
    axes[0].set_ylabel("Polarization")
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)

    # Nearest-neighbor distance+KS test
    sns.kdeplot(real[1], ax=axes[1], label="Dataset", fill=True, color='blue')
    sns.kdeplot(sim[1], ax=axes[1], label="Simulation", fill=True, color='orange')
    ks_stat, p_val = ks_2samp(real[1], sim[1])
    axes[1].annotate(f"KS-dist: {ks_stat:.3f}\np-val: {p_val:.2e}", xy=(0.6, 0.8), xycoords='axes fraction')
    axes[1].set_title("B. Nearest-neighbor distance ")
    axes[1].set_xlabel("Distance")
    axes[1].legend()

    # Anisotropy Map 
    sim_rel = np.array(sim[2])
    hb = axes[2].hexbin(sim_rel[:, 0], sim_rel[:, 1], gridsize=40, cmap='YlGnBu', mincnt=1)
    axes[2].set_aspect('equal')
    axes[2].set_title("C. Interaction Anisotropy(Boids)")
    axes[2].set_xlabel("Lateral distance (x')")
    axes[2].set_ylabel("Forward distance (y')")
    plt.colorbar(hb, ax=axes[2], label='Neighbor Density')

    plt.tight_layout()
    plt.savefig("boids_validation_real.pdf") 
    plt.show()

if __name__ == "__main__":
    config = {"num_boids": 255, "width": 1476, "height": 846}
    real_data, sim_data = experiment("schooling_frames.json", config)
    plot_science_report(real_data, sim_data)
