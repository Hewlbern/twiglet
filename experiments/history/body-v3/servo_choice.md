# Arm servo choice for body v3: Feetech STS3032 (C001)

## The problem
v2 used six STS3215s in the arms (45.2 × 24.7 × 35 mm, 55 g each). Two STS3215 cases side by side made the shoulders 213 mm wide, so head/shoulder came out at 0.80 against about 1.16 in the photo. v3 keeps the same 3 DOF per arm (shoulder pitch, elbow, gripper) on the same Feetech TTL bus, but moves them to a micro bus servo.

## Candidates checked (real parts, real sources)

| | **STS3032-C001 (chosen)** | SCS0009 | STS3215-C001 (v2, reference) |
|---|---|---|---|
| Size (mm) | 23 × 12 × 27.5 body (32 mm over the mounting ears; 31.9 to the spline top) | 23.2 × 12.1 × 25.25 | 45.2 × 24.7 × 35 |
| Mass | 20 g (datasheet 20.6 ± 1 g) | 13.2 g | 55 g |
| Stall torque | 4.5 kg·cm = 0.441 N·m @ 6 V (3.5 kg·cm @ 4.8 V) | 2.3 kg·cm = 0.23 N·m @ 6 V | 19.5 kg·cm = 1.91 N·m @ 7.4 V |
| Rated torque | 1.5 kg·cm = 0.147 N·m | 0.7 kg·cm = 0.069 N·m | about 0.49 N·m |
| No-load speed | 0.09 s/60° @ 6 V (111 rpm) | 0.1 s/60° @ 6 V | 0.192 s/60° @ 7.4 V |
| Current (stall / rated / idle) | 1.2 A / 0.4 A / 0.15 A | – | 2.7 A stall |
| Feedback / range | 12-bit magnetic encoder, 360° | 10-bit potentiometer, 300° | 12-bit magnetic, 360° |
| Gears / case / bearings | metal gears, aluminium case, 2 ball bearings | metal gears, plastic case, no bearings | metal gears, plastic case |
| Protocol | **STS TTL (same as the STS3215 legs/neck)** | SCS protocol (different register map) | STS TTL |
| Voltage | 4.8–6 V typical, 4–7.4 V input range | 4–7.4 V | 6–7.4 V |
| Price | US$32.99 BABSCO; €37.20 Eckstein; US$38.68 DrUAV; US$40 AIFITLAB; US$47.63 RobotShop (C036) | US$9 Seeed; €13 Eckstein; US$19.75 Abra | €24.35 Eckstein; US$23.99 OpenELAB |

Sources:
- STS3032 Feetech datasheet: https://akizukidenshi.com/goodsaffix/STS3032%20SPEC.pdf (dimension drawing on page 6)
- STS3032 Feetech product page: https://www.feetechrc.com/6v-45kg-magnetic-code-360-degree-serial-bus-steering-gear.html
- STS3032 retailers: https://shop.babsco.com/feetech-sts3032-4-5kg-compact-smart-servo-c001 , Eckstein, DrUAV, AIFITLAB, RobotShop
- SCS0009: https://www.feetechrc.com/en/6v-23kg-serial-bus-steering-gear_65522 , https://www.seeedstudio.com/Feetech-SCS0009-Servo-p-6535.html
- STS3215: https://eckstein-shop.de/Feetech-STS3215-74V-19kgcm-plastic-case-metal-gear-magnetic-code-dual-shaft-TTL-serial-servo , https://openelab.com/products/feetech-sts3215-c001-servo-7

## Why the STS3032
1. **Same bus and protocol as the rest of the robot.** STS packets, the same SDK and registers, and a 12-bit 360° magnetic encoder, so the arm code stays as it is. The SCS0009 would need the SCS protocol and a 10-bit potentiometer servo on the same line.
2. **Enough torque with margin.** The worst static load (arm held horizontal, shoulder) is 0.046 N·m with the v3 printed arm (MuJoCo gravity torque). That is 31% of the 0.147 N·m rated torque and 10% of stall. The SCS0009 would already be at 64% of its 0.069 N·m rating before lifting anything.
3. **It hits the width target.** Case 12 mm thick, arm column 37 mm deep: shoulder width 146 mm, head/shoulder **1.166** (target 1.16).
4. Metal gears, 2 ball bearings and an aluminium case: it survives falls onto the arms better than the plastic, bearing-less SCS0009.
5. **Mass.** Six STS3032s are 210 g lighter than six STS3215s. That is a large part of why v3 weighs 2.17 kg against 2.42 kg for v2.

## Power
The datasheet gives 4.8–6 V typical and a 7.4 V maximum. The 2S pack is 8.4 V when full, which is above that maximum. **Put a 6 V buck regulator on the arm branch** (for example Pololu D36V50F6, 6 V 5.5 A). Share the data line and ground with the STS3215 bus. Six arm servos draw 0.9 A at idle; three waving hard draw about 2–3 A peak.

## Can it carry the Feetech grippers? What changes
- **The photo's Feetech gripper modules are STS3215-sized, and v3 does not reuse them.** An STS3215 gripper (≈55 g servo + ≈15–20 g brackets) at the wrist would:
  - raise the shoulder static load to about 0.09 N·m (60% of rated);
  - leave only about 40 g of continuous payload;
  - add 25 mm of width at each wrist, which breaks the slim silhouette.
- **v3 uses an STS3032 as the gripper actuator** in a black printed housing (`v3_gripper_housing_*`), with a printed fixed finger and a moving finger on the horn (`v3_finger_moving_*`).
  - Finger length is 50 mm from the horn axis. Tip force is about 8.8 N at stall and 2.9 N continuous. The STS3215 gripper gives about 38 N.
  - That is plenty for light objects (a ball, a card, a small plush) but it is not a strong gripper.
- **Payload, arm horizontal, measured at the fingertips (about 125 mm from the shoulder):**
  - about 80 g continuous (rated torque);
  - about 320 g brief (stall).
  - Lower-arm poses carry much more.
- **The old STS3215 arm links, fingers and v2 shoulder mounts are not reused.** All arm parts are new (see `stl/v3_upper_arm_*`, `v3_forearm_*`, `v3_gripper_housing_*`, `v3_finger_moving_*`).

## Heat (sim, `sim/arm_heat_v3.json`)
Same commanded motion on v2 and v3: right arm forward at about 65° waving ±20° at the shoulder and ±10° at the elbow, left arm swinging 5–55°.

| Wave frequency | Worst RMS / rated | Copper loss per servo | Verdict |
|---|---|---|---|
| 0.5 Hz | 0.74× | 0.28 W | fine for continuous use |
| 0.8 Hz | 0.99× | 0.51 W | at the rated limit: bursts only, not continuous |
| 1.5 Hz | 1.63× | 1.36 W | will overheat. Limit to a few seconds, or cap continuous waving at about 0.6 Hz in software |

STS3215 arms (v2) on the same motion ran at 0.35× / 0.58× / 1.39× rated at 0.5 / 0.8 / 1.5 Hz, so v2 would also overheat at 1.5 Hz. Sustained waving is the one thing the smaller servo does noticeably worse. Copper loss is (τ_rms / Kt)² · R, with Kt 0.343 N·m/A and R 2.8 Ω for the STS3032. The arm armature in the sim (0.004 kg·m²) is an estimate, so treat these as ±30%.
