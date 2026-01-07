### Source: https://data.mendeley.com/datasets/bszk9ztryp/1

This dataset consists of a couple separate csv files that contain all the necessary data to create figures 1-3 and run the analyses in our manuscript. The columns of each dataset are described in detail below.

final_sizedat.csv
----------------------
Dataset with the shiner and pike bodysizes
batch: the experimental batch (1,2)
trial: unique trial number
type: pike or shiner
BL: fishes' body length in cm


final_fig1dat.csv
----------------------
Dataset used to generate Figure 1A and B
frame: frame of video (trial recordings were automatically divided in smaller sequential videos)
relattack_ms: time relative to frame of attack in miliseconds
id: shiner ID number or whether the data corresponds to the pike or group centroid
target: whether the shiner was the individual that was targeted that trial or not
x: x-position in cm
y: y-position in cm
xpix: x-position in tank in pixels
ypix: y-position in tank in pixels
hx: x-component of orientation vector
hy: y-component of orientation vector
cluster: cluster the shiner belonged to
relcent_dis: distance to the group centroid


final_reltoselfdat.csv
----------------------
Dataset with pikes' positioning data relative to that at the moment of attack. Used also for creating Figure 2A.
frame: frame of video (trial recordings were automatically divided in smaller sequential videos)
relattack_ms: time relative to frame of attack in miliseconds
x_reltoself: x-position in cm relative to pike's position at the frame of attack
y_reltoself: y-position in cm relative to pike's position at the frame of attack
hx_reltoself: x-component of motion vector relative to pike's position at the frame of attack
hy_reltoself: y-component of motion vector relative to pikes' position at the frame of attack


final_fig3dat.csv
----------------------
Dataset to generate plots of Figure 3.
id: shiner ID number or whether the data corresponds to the pike or group centroid
target: whether the shiner was the individual that was targeted that trial or not
relcent_dis: relative distance to the group centroid (cm)
onhull: whether an individual is part of the group hull or not (i.e. the outermost individuals of the group)
medIID: fish's median inter-individual distance to all other group members (cm)
misalign: Difference in orientation angle (in degrees) between the shiner and its group mates within 10cm
misalign_6nb: Difference in orientation angle (in degrees) between the shiner and its six nearest group mates
voronoi_area_log: Area (cm2) around a shiner closest to that individual and not another individual, limited to the boundaries of the testing arena (log-transformed)
LDOD_log: VA limited to a max radius of 10 cm from the shiner (log-transformed)
frontback_cd: Shiners’ distance from the group centroid in the plane of the group average orientation (+: in front of centroid; -: behind centroid)
vis_wgtdegree: The proportion of each shiner’s vision occupied by conspecifics
relpike_dis: relative distance to the pike (head centroid; cm)
relpike_angle_abs: relative absolute angle to the pike positioned at the origin pointed up
relpike_orient_abs: relative absolute orientation to that of the pike (degrees)
vis_pikeseeshiner: Pike’s field of view occupied by the individual shiner (deg)


final_attackdata.csv
----------------------
Full attack dataset used for the majority of analyses
batch: the experimental batch (1,2)
exposure: how often the fish in this trial had been exposed to the pike (including current trial)
trial: unique trial number
attempt: attack attempt during the trial
success: if the attack was successful or not
pike: id of the pike
id: ID of the fish (or whether the data corresponds to the "pike" or group centroid ("cnt"))
bl: standard body length (cm)
preyfocused: filter for prey-focused approach, i.e. only attacks where the pike attacked the main cluster and the shiner being part of the main cluster
predatorfocused: filter for the predator-focused approach, i.e. if the shiner was part of the preyfocused approach and on top of that in the region 4 cm left or right of the pike and max 15cm in front.
target: whether the shiner was the individual that was targeted that trial or not
pike_clustersizerel: the relative size of the cluster the pike attacked (1 is maximum)
pike_medspeed_befBL: median speed of the pike until the frame of attack (BL/s; based on smoothed data)
pike_relspeed100ms: pikes' change in speed relative to 0.1s before the attack (cm/s)
pike_maxspeed: maximum speed of the pike throughout the attack (cm/s; based on smoothed data)
pike_maxaccel: maximum acceleration of the pike throughout an attack (m/s2; based on smoothed data)
pike_walldis: pike's distance to the nearest wall (cm)
pike_shinervis: Pike's field of view occupied by the individual shiner (deg)
target_maxspeed_bef: Targeted shiner's maximum speed (based on smoothed data) in the 0.5s until the time of attack (cm/s)
target_maxsaccel_bef: Targeted shiner's maximum acceleration (based on smoothed data) in the 0.5s until the time of attack (m/s)
target_maxturn_bef: Targeted shiner's maximum orientation change in the 0.5s until the time of attack (deg)
gr_nclusters: number of clusters
gr_largestcluster: size of largest cluster (1 is maximum)
gr_iid: average inter-individual distance among all shiners in the main cluster (cm)
gr_pol: polarisation of the shiners in the main cluster
gr_speedc: speed of the group centroid (cm/s)
gr_rot: group rotation of the main cluster
x: x-position (cm)
y: y-position (cm)
hx: x-component of orientation vector
hy: y-component of orientation vector
speed: movement speed (cm/s)
speedsm: movement speed based on smoothed data (cm/s)
accel: acceleration (m/s2)
accelsm: acceleration based on smoothed data (m/s2)
hulldis: distance from the group hull (cm)
onhull: whether an individual is part of the group hull or not (i.e. the outermost individuals of the group)
voronoi_area_log: Area (cm2) around a shiner closest to that individual and not another individual, limited to the boundaries of the testing arena (log-transformed)
LDOD_log: VA limited to a max radius of 10 cm from the shiner (log-transformed)
misalign: Difference in orientation angle (in degrees) with group mates within 10 cm
misalign_6nb: Difference in orientation angle (in degrees) with 6 nearest group mates
medIID: shiner's median inter-individual distance to all other group members (cm)
nnd: shiner's average nearest-neighbour distance (cm)
vis_wgtdegree: The proportion of each shiner’s vision occupied by conspecifics
relcent_x: relative x-position to the group centroid (cm)
relcent_y: relative y-position to the group centroid (cm)
relcent_dis: relative distance to the group centroid (cm)
relcent_dis_rscale: relative distance to the group centroid ranked and scaled 0 to 1
frontback_cd: Shiners’ distance from the group centroid in the plane of the group average orientation (+: in front of centroid; -: behind centroid)
frontback_rscale: Shiners’ distance from the group centroid in the plane of the group average orientation ranked and scaled 0 to 1
relpike_x: relative x-position to the pike positioned at the origin pointed up (cm)
relpike_y: relative y-position to the pike positioned at the origin pointed up (cm)
relpike_dis: relative distance to the pike (head centroid; cm)
relpike_angle: relative angle to the pike positioned at the origin pointed up
relpike_angle_abs: relative absolute angle to the pike positioned at the origin pointed up
relpike_orient: relative orientation to that of the pike (deg)
relpike_orient_abs: relative absolute orientation to that of the pike (deg)
relpike_chead: relative heading of the group centroid to that of the pike (deg)
relpike_cvel: relative speed of the group centroid to that of the pike (cm/s) 
relpike_cyvel: relative speed of the group centroid to that of the pike in the plane of the pike's orientation (cm/s)