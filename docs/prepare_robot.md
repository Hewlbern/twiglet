# Prepare the robot (from design to MuJoCo)

> Upstream's version goes from the Onshape design to MuJoCo through onshape-to-robot: see [upstream/prepare_robot.md](upstream/prepare_robot.md). Twiglet has no Onshape document, so its model was made differently.

## Our model

- **Model file:** `mini_bdx/robots/twiglet_v334/twiglet_v3.xml`, with its meshes in `meshes/`.
  - 19 actuators: 10 legs, head_pitch/yaw/roll, and shoulder/elbow/gripper L/R.
  - 2.753 kg in total.
- **Current robot with wig v3.44:** `twiglet_v3_wig344.xml` (2.753 kg, head 0.814 kg), made by `experiments/twiglet_sim/tools/make_v334_wig.py`: the v3.34 model with the head inertial and head collision box of the hair c14 (v3.44) model `hair_c14_v344.xml`. That script runs from the repo (it only reads three files in `models/`). The 52 versions and variants are in `experiments/twiglet_sim/models/`.
- **How it was built:**
  - `experiments/twiglet_sim/tools/gen_mjcf_v3.py` built the v3 MJCF from the Open Duck Mini v2 kinematics, using the mass rules of our earlier body-v2 model plus new part kinds (STS3032 cases, light-print head, displays).
  - Each later version edited it. For example, `experiments/twiglet_sim/tools/mass_v334.py` adds the changed-part mass deltas (solid PLA, 1.24 g/cm3) to the bodies they ride on.
  - The mass bookkeeping is in `mini_bdx/robots/twiglet_v334/mass_v334.json`.
- **Reference only:** `gen_mjcf_v3.py`, `mass_v334.py` and `make_xml_variant.py` read caches and earlier versions from the original build workspace. They don't run on their own from this repo (TODO: make them self-contained).
- **Mass assumptions:** the head is modelled at 2 walls + 8 % infill (wig 4.5 % lightning), with the head shells, snout and chin collars in PETG at 1.27 g/cm3 and 25 g of rear ballast. Print exactly that, or the model no longer matches.
- **STS3032 arm actuators:**
  - ctrlrange is clipped to ±0.441 N·m (stall at 6 V).
  - The armature (0.004) is an estimate. The STS3032 has not been identified with BAM (TODO).
