# Contributing

Issues and pull requests are welcome: print reports, build photos, BOM prices, fixes to the guides, new sims or checks. The robot has **not been built yet**, so a report from a real print or build is the most useful contribution of all.

## Setting up

```bash
git clone https://github.com/Hewlbern/twiglet.git
cd twiglet
python3 -m venv .venv && source .venv/bin/activate
pip install mujoco numpy trimesh python-fcl scipy manifold3d pyvista matplotlib
cd experiments/twiglet_sim && ./run_all.sh twiglet_v3_v334_wig344.xml mycheck   # ~2 min: standing, push, neck load, both gaits
```

Before you open a pull request that changes a part or the model, run the checks that match the change (see [experiments/README.md](experiments/README.md)) and compare them with the reference results in each `results/` folder.

## Directory layout

```
twiglet/
├── print/                      # stock Open Duck Mini v2 STLs (unchanged, from upstream)
│   └── mods/Twiglet/         #   everything new: print-oriented STLs per version
│       ├── body_v3.34/         #     torso, kilt, arms, covers, boots (+ print sheet)
│       ├── head_v3.30/         #     head shells, nose, eye bezels and carriers
│       ├── wig_v3.44/          #     the one-piece hair piece
│       └── source/             #     .blend files + Blender/Python build scripts (provenance)
├── mini_bdx/robots/twiglet_v334/   # MuJoCo model (MJCF + visual meshes)
├── experiments/
│   ├── twiglet_sim/               # MuJoCo sims: standing, push, neck load, gaits, arm heat
│   ├── twiglet_geom/              # mesh checks: head range, arm sweeps, kilt swing, print files, renders
│   ├── twiglet_eyes/              # ESP32-S3 eye firmware + Pi helper
│   └── history/                # read-only archive of every earlier version's results
├── docs/                       # BOM, print and assembly guides, images, upstream docs
├── BEST_WALK_*_PARAMS_*.npy    # the shipped gait parameter vectors
├── NOTICE, LICENSE             # Apache-2.0 + third-party notices
└── README.md
```

## Where a new file goes

| What it is | Where |
|---|---|
| A new or changed printable part | `print/mods/Twiglet/<part>_v<version>/` as an STL in print orientation (z = 0 on the bed), plus a short notes file |
| Its source (.blend, build script) | `print/mods/Twiglet/source/blender/` or `source/scripts/<part>_v<version>/` |
| A new sim model | `experiments/twiglet_sim/models/`, built by a script in `experiments/twiglet_sim/tools/` so it can be regenerated |
| A sim or check | `experiments/twiglet_sim/` or `experiments/twiglet_geom/`, with a usage line at the top and outputs to `out/` (gitignored) |
| A result that should become the reference | copy it by hand into that folder's `results/` and update the README table |
| Images for the docs | `docs/images/` (renders) or `docs/images/assembly/` (made by `render_assembly.py`) |

## Conventions

- **Files under 100 MB** (GitHub's limit); flag anything over 25 MB in the README.
- **No absolute paths** (`/Users/...`, `/home/...`) in code or docs. Use paths relative to the script, or an environment variable (`TWIGLET_XML`, `TWIGLET_OUT`, `BLENDER`, `PYTHON`, `WORK`).
- **No personal data** in files or file metadata: no emails, addresses, phone numbers or tokens. Only use your GitHub noreply address as the commit email.
- **Only images you have the rights to.** Your own renders and photos are fine. Do not add third-party photos or artwork, even as reference.
- **Required print settings are part of the design.** The sims assume the head and hair infill in `docs/print_guide.md`; if you change a print setting or a part's mass, re-run the neck-load (`quick_static.py`, keep ≥ 2× hold) and gait checks.
- **Keep `experiments/history/` read-only.** It is the record of what was run.
- Scripts marked *provenance only* need the original build workspace and are kept to document how a file was made.

## Licence

By contributing you agree that your contribution is licensed under the Apache License 2.0, the same as this repository ([LICENSE](LICENSE)). If you add third-party material, add it to [NOTICE](NOTICE) with its source, copyright and licence.
