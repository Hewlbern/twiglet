# history: archived results of every earlier version

This is a read-only archive. It holds the results of each design iteration, copied from the original build workspace so the numbers behind every decision are in the repo:
- `body-v2` … `body-v3.34-body`: per body version. `sim/` has results_v3.json, walk_v3*.json, compare_*.md, logs and the plots. The collision/measure json and the READMEs and print notes are also here.
- `hair-v3.33` … `hair-v3.41`: the wig iterations (IoU fits, arm/head checks, sims, STATUS logs).
- `head-v2`, `head-v3-digital-eyes`: the head designs before v3.30.
- `tmp_eye_c_head_agent`: the eye-coverage work for head v3.30.

What it contains:
- 1239 unique files (19 MB): json/txt/md/csv/log under 3 MB, the sim/simC PNG plots under 1.5 MB, and 18 short mp4 walk/push/head-arm videos (v2 to v3.2, each under 2 MB). There are no v3.3x videos.
- Exact duplicates (same md5) are stored once. [`INDEX.csv`](INDEX.csv) maps every original path (8408 rows) to the stored copy.
- Not archived: meshes, Blender files, renders, caches and the ~10 MB GIFs.

[`sim_history.md`](sim_history.md) / `.csv` is the per-version table (mass, standing margin, e-margin, head-pitch peak, gait success and speed). Rebuild it with `python ../tools/history_table.py`.

Some logs and notes in here (about 50 files) refer to the original build workspace as `$WORK/...` (the absolute paths were replaced by that placeholder). They document what was run; nothing in here is meant to run. The runnable versions are in `../twiglet_sim` and `../twiglet_geom`.
