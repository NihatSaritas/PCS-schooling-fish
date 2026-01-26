# PCS-schooling-fish

A Python-based boids simulation modeling schooling fish behavior with predator interactions.

## Usage

Run the main simulation:
```bash
python boids_hunteradams.py
```

*Note: `boids_simulation.py` is an earlier prototype - use `boids_hunteradams.py` for the current implementation.*

## Parameters

### Boid Parameters
| Parameter | Default | Description | Min | Max | Type
|-|-|-|-|-|-|
|**num_boids**|50|Number of fish in the simulation|1|$10^5$|<code>int</code>
|**visual_range**|40|Distance at which boids can see neighbors|||
|**protected_range**|8|Minimum distance maintained between boids|||
|**centering_factor**|0.0005|Strength of cohesion (moving toward center of mass)|||<code>float</code>
|**avoid_factor**|0.07|Strength of separation (avoiding collisions)|||<code>float</code>
|**matching_factor**|0.05|Strength of alignment (matching velocity)|||<code>float</code>
|**maxspeed**|3|Maximum boid speed|||
|**minspeed**|2|Minimum boid speed|||
|**turn_factor**|0.2|Edge avoidance strength <br> (this is an example of newline in <br> table)|$10^{-6}$|1|<code>float</code>


### Field of View (Katz et al. inspired)
| Parameter | Default | Description | Min | Max | Type
|-|-|-|-|-|-|
|**fieldofview_degrees**|170°|Field of view (small blind zone behind)|||
|**front_weight**|0.3|Extra influence of neighbours in front  (‘front–back asymmetry in social interactions’)|||<code>float</code>
|**speed_control**|0.03|Speed change from crowding (computed from neighbour density ahead vs behind)|||<code>float</code>
|**turning_control**|0.05|Turning from left/right density difference (computed in the fish’s body frame)|||<code>float</code>
|**max_turn**|0.15|Limits turning per step to keep motion smooth|||<code>float</code>

### Predator Parameters
| Parameter | Default | Description | Min | Max | Type
|-|-|-|-|-|-|
|**num_preds**|1|Number of predators|||<code>int</code>
|**visual_range_pred**|60|Predator vision range|||
|**predatory_range**|100|Range where boids flee from predators|||
|**eating_range**|20|Range where a predator can eat a boid|||
|**predator_weight**|0.1|Strength of predator attraction/avoidance|||<code>float</code>
|**avoid_factor_pred**|0.1|Predator-to-predator avoidance|||<code>float</code>
|**maxspeed_pred**|3|Maximum predator speed|||
|**minspeed_pred**|2|Minimum predator speed|||
|**turn_factor_pred**|0.2|Predator edge avoidance strength|||<code>float</code>

### Display
| Parameter | Default | Description | Min | Max | Type
|-|-|-|-|-|-|
|**width**|640|Canvas width|||
|**height**|480|Canvas height|||
|**margin**|20% of <code>max(width, height)</code>|Boundary margin for edge avoidance|||
