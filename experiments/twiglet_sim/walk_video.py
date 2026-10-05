"""Render the best gait from walk_search (nominal model) to GIF/MP4 and save torque traces. Usage: python walk_video.py v2|stock"""
import sys, os, json, math, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from simlib import *
from episode import run
from walk_search import KEYS
V = sys.argv[1]; SUF = "_eff" if "--eff" in sys.argv else ""
best = np.load(params_path(SUF)); p = dict(zip(KEYS, best)); p["ramp"] = 1.0
m, d = load(V); sv = Servo(m); g = Gait(sv.names, p, V); q0 = stance(sv.names, p["crouch"], lean=BASE_LEAN[V])
reset(m, d, q0); rec = Recorder(sv.names, sv.stall); vid = Video(m, dist=1.05, az=125, el=-12)
com = []
info = run(m, d, sv, lambda t, r, gy: g(t, r, gy, q0), 10.0, V, rec=rec, video=vid, on_step=lambda t, dd: com.append([t, *dd.subtree_com[1]]))
vid.save(os.path.join(OUT, f"walk_{V}{SUF}.gif"), fps=25)
try: vid.save(os.path.join(OUT, f"walk_{V}{SUF}.mp4"), fps=25)
except Exception as e: print("mp4", e)
np.savez(os.path.join(OUT, f"walk_{V}{SUF}_trace.npz"), t=np.array(rec.t), tau=np.array(rec.tau), names=np.array(sv.names), com=np.array(com))
print(V, info)
