# Twiglet body v3.5: servo / electronics BOM delta

| Item | v3.4 | v3.5 | Note |
|---|---|---|---|
| Feetech STS3215 (7.4 V) | 14 (10 legs + neck pitch + head pitch/yaw/roll) | **13** (10 legs + head pitch/yaw/roll) | low neck-pitch servo removed; head stack on a fixed neck post |
| Feetech STS3032 (arms, 6 V buck) | 6 | 6 | unchanged |
| Bus servo IDs | 20 | 19 | drop the neck-pitch ID from the controller config |
| Printed: neck sheets L/R (neck_sheet_L/R) | 2 | 0 | not needed (no neck-pitch servo) |
| Printed: head_yaw_to_roll | stock | **v35_head_yaw_to_roll** | re-cut: roll horn wall + rear bearing arm 3 mm rearward (not a head part) |
| Printed: torso_frame / torso shell front+back | v3.4 | v3.5 | fixed head-pitch cup cradle, front plate 12 mm rearward, sleeve notches; slimmer cone |
| Head parts (shells, fringe, bezels, carriers, chin collars, roll mount) | - | unchanged | no reprint |

Everything else (Pi Zero 2W, Waveshare bus board, BNO055, 2 x 18650 + BMS + charger, switch) is unchanged.
