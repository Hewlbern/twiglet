# Twiglet mod

A Twiglet look for Open Duck Mini v2: a wooden-ball head with digital eyes, a one-piece wig under a felt hat, a slim torso cone with a leaf kilt, and two 3-DOF STS3032 arms with grippers.

Upstream mods ship `.step` and `.3mf` files. This mod was made in Blender, so it ships STLs (already in print orientation) plus `.blend` and Python sources instead. TODO: export `.3mf` plates.

<table>
  <tr>
    <td> <img src="../../../docs/images/assembly/s15_complete_front.png" alt="1" width="400px" ></td>
    <td> <img src="../../../docs/images/wig_v344_closeup.png" alt="2" width="400px" ></td>
   </tr> 
</table>

| Folder | Version | Contents |
|---|---|---|
| `body_v3.34/` | body v3.34 (final) | 50 STLs: torso frame and shells, hip cradle and brackets, thigh sheets and spacers, shin covers, boots and cuffs, arms and grippers, leaves and vines, kilt band and 10 petals. Also `print_sheet_body_v334.md`, `CHANGED_PARTS_v334.md`, `README_v334.md` and `metrics_v334.json` |
| `head_v3.30/` | head v3.30 (final) | 10 STLs: head_upper/lower, snout, chin collars, eye bezels, display carriers, `head_yaw_to_roll` (a neck part; print it instead of the stock one). Also `print_note_head_v330.md`, `README_v330.md` and the print/mesh reports. The old v3.30 wig is left out on purpose. |
| `wig_v3.44/` | hair v3.44 (c14, final) | `FINAL_WIG.stl` (print-oriented; yellow PLA, 4.5 % lightning, 186.2 g), `FINAL_WIG_model_frame.stl` (same mesh in the head model frame, for the sims and checks; do not print this one), `NOTES_wig_v344.md`, `final_export.json`. The v3.40 notes are in `experiments/history/hair-v3.40/`. |
| `source/blender/` | | `body_v334.blend` (59 MB, flagged > 25 MB) and `hair_v344.blend` (3.7 MB, object `FINAL_WIG_v344_c14`). `head_v330.blend` (194 MB) is **not included** because it is over GitHub's 100 MB limit (TODO). |
| `source/scripts/` | | Blender/Python build scripts: `body_v3.34/`, `head_v3.30/` (with `README_blender.md`) and `wig_v3.44/` (with `variants/c14.*`, the edit set for the final wig). They are provenance: some need the original build workspace (`$WORK`) and the base `base_wig_v330.blend`, which is not included. |

Print settings: [docs/print_guide.md](../../../docs/print_guide.md). Assembly: [docs/assembly_guide.md](../../../docs/assembly_guide.md). BOM: [docs/BOM.md](../../../docs/BOM.md).

Stock Open Duck Mini v2 parts that are still used: feet, `roll_motor_top/bottom`, knee-to-ankle sheets, `leg_spacer`, `head_pitch_to_yaw` and `head_roll_mount` (in `print/`).
