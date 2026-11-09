import sys, os, json, math, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from simlib import *
from episode import run
V="v3"; m, d = load(V); sv = Servo(m); N = sv.names
q = stance(N, 0.30, lean=BASE_LEAN[V]); reset(m, d, q)
run(m, d, sv, lambda t, r, g: q, 3.0, V)
i = N.index("head_pitch"); j = m.joint("head_pitch").id; b = m.jnt_bodyid[j]
ax = d.xaxis[j]; anc = d.xanchor[j]; com = d.subtree_com[b]; M = m.body_subtreemass[b]
tg = np.dot(np.cross(com - anc, M * np.array([0, 0, -9.81])), ax)
print(json.dumps(dict(ctrl=round(float(abs(d.ctrl[i])),4), grav=round(float(tg),4), mass=round(float(M),4), com_rel=((com-anc)*1000).round(1).tolist(), axis=ax.round(3).tolist(), head_mass=float(m.body_mass[m.body("head_assembly").id]))))
