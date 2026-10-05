# twiglet_v334

This is the MuJoCo model of the Twiglet robot (body v3.34, head v3.30). It sits where upstream keeps `mini_bdx/robots/open_duck_mini_v2/`.

- `twiglet_v3.xml`: the MJCF, with 19 position actuators:
  - left/right `hip_yaw`, `hip_roll`, `hip_pitch`, `knee`, `ankle`
  - `head_pitch`, `head_yaw`, `head_roll`
  - `shoulder_L/R`, `elbow_L/R`, `gripper_L/R`
- `twiglet_v3_wig344.xml`: **the current robot**, the same model with the head inertial of the wig v3.44 (hair c14) head: 2.753 kg total, head 0.814 kg. It is a copy of `experiments/twiglet_sim/models/twiglet_v3_v334_wig344.xml` (made by `experiments/twiglet_sim/tools/make_v334_wig.py`).
- Total mass of `twiglet_v3.xml`: 2.753 kg.
- `meshes/`: 60 STL visual meshes. Contact is only the floor vs 4 boxes (trunk, feet, head); part-to-part clearance is checked on the print meshes in `experiments/twiglet_geom/`.
- `mass_v334.json`: the per-part mass deltas applied for v3.34.
- There is no URDF or onshape-to-robot `config.json`: the model was not made from Onshape (TODO, if the runtime/playground needs them).
- The 25 g head ballast is included in both. `twiglet_v3.xml` has the older v3.30-era fringe in the head mass; `twiglet_v3_wig344.xml` has wig v3.44.
- All the other versions (body v3.20–v3.34, infill sweeps, hair series) are in `experiments/twiglet_sim/models/`.
