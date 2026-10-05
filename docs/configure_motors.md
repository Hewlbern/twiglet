# Configure the motors

> This is based on the [Open Duck Mini v2 guide](https://github.com/apirrone/Open_Duck_Mini/blob/v2/docs/configure_motors.md). A verbatim copy is in [upstream/configure_motors.md](upstream/configure_motors.md).

> This sould be done independently on each motor *before* builiding the duck.
>
> During the process, the motor will move to its zero position. You can then install the horn while trying to align it the best you can. (Don't worry if it's not perfect, we will compensate for that later)

Clone and install (`pip install -e .`) the runtime repo on the `v2` branch : `https://github.com/apirrone/Open_Duck_Mini_Runtime`

Then for each motor, run the following command : 

```bash
python configure_motor.py --id <id>
```

The STS3215 IDs are upstream's, minus `neck_pitch`: Twiglet has had no neck-pitch servo since v3.5, so there are 13 STS3215s.

```python
{
    "left_hip_yaw": 20,
    "left_hip_roll": 21,
    "left_hip_pitch": 22,
    "left_knee": 23,
    "left_ankle": 24,
    # "neck_pitch": 30,  # not used in twiglet
    "head_pitch": 31,
    "head_yaw": 32,
    "head_roll": 33,
    "right_hip_yaw": 10,
    "right_hip_roll": 11,
    "right_hip_pitch": 12,
    "right_knee": 13,
    "right_ankle": 14,
}
```

The arm servos are 6× Feetech **STS3032**. They use the same STS TTL protocol and bus, but have to be powered from the **6 V** branch, not straight from the 2S pack.

```python
{
    # TODO: arm servo IDs not decided. The joint names below are the ones in the sim model.
    "shoulder_L": None,
    "elbow_L": None,
    "gripper_L": None,
    "shoulder_R": None,
    "elbow_R": None,
    "gripper_R": None,
}
```

- TODO: check that `configure_motor.py` works on the STS3032. The protocol and register map are said to be the same as the STS3215, but this has not been tested.
