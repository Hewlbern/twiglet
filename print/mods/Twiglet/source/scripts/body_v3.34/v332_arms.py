"""v3.32 arms/grippers (Blender 4.2: blender -b body_v332.blend -P v332_arms.py).
Photo: thin wooden arm segments, exposed black servo at the elbow, a BIG black gripper box (~58 x 50 x 35 mm) with two long fingers.
 - gripper_housing_L/R: v3.9/rev C housing (asm frame) + its fixed finger stretched 14 mm along the arm axis, unioned with a 1.4 mm-wall
   hollow box shell (local frame of the tilted forearm: x -10..20, outward 0..50 from the housing's inner face, top = housing top, 56 tall,
   3 mm rounded edges) minus the moving finger + horn sweep (-14..64 deg, 4 deg steps) so the gripper still opens over its -10..60 range.
 - finger_moving_L/R: stretched 14 mm (same plane as the fixed finger).
 - elbow_sleeve_L/R: geometry unchanged, re-specified in black (exposed-servo look).
Writes collection ARMS_v332 (asm frame) and out/asm/*.stl + out/stl/v332_*.stl (print frame of the v3.9 parts)."""
import bpy, bmesh, os, sys, math, json
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
C = L.coll("ARMS_v332"); TMP = L.coll("TMP_v332_arms")
DF = float(os.environ.get('DF', 14.0)); DTH = float(os.environ.get('DTH', 22.5));  # stretch plane perpendicular to the finger axis d (a z-plane left 0.1 mm slivers)
W = 1.4; O0 = float(os.environ.get('BOX_O0', -6.0)); O1 = float(os.environ.get('BOX_O1', 42.0))
log = {}
for s, sg in (("L", 1), ("R", -1)):
    J = Vector((4.0, sg * 65.5, -42.2)); a = Vector((0.0, -0.98, -0.17 * sg)).normalized()
    o = (-a if s == "L" else a).normalized(); d = Vector((1, 0, 0)).cross(o).normalized()
    if d.z > 0: d = -d
    hs = L.imp(os.path.join(L.REF, f"gripper_housing_{s}.stl"), f"gripper_housing_{s}_v332", C)
    fm = L.imp(os.path.join(L.REF, f"finger_moving_{s}.stl"), f"finger_moving_{s}_v332", C)
    hn = L.imp(os.path.join(L.REF, f"s32horn_gripper_{s}.stl"), f"tmp_horn_{s}", TMP)
    v0h = hs.data.vertices[:]
    # local coords of the housing (x, o, d) relative to J
    loc = lambda p: (p.x, (p - J).dot(o), (p - J).dot(d))
    H = [loc(v.co) for v in hs.data.vertices]
    top_d = min(h[2] for h in H); o_in = min(h[1] for h in H if h[2] < top_d + 20)
    hs0 = L.dup(hs, f'tmp_hs0_{s}', TMP)
    # 1. stretch both fingers DF mm along d beyond the plane (p-J).d = DTH (~z -64)
    for ob in (hs, fm):
        for v in ob.data.vertices:
            if (v.co - J).dot(d) > DTH: v.co = v.co + d * DF
        ob.data.update()
    # 2. hollow box shell in the forearm-tilted frame
    def lbox(name, x0, x1, o0, o1, d0, d1, bev):
        b = L.box(name, (x0, o0, d0), (x1, o1, d1), TMP, bevel=bev)
        Mx = Matrix(((1, 0, 0, 0), (0, o.x, d.x, 0), (0, 0, 0, 0), (0, 0, 0, 1)))
        R = Matrix(((1, 0, 0), (0, 0, 0), (0, 0, 0)))
        R = Matrix((Vector((1, 0, 0)), o, d)).transposed()     # columns: x, o, d
        for v in b.data.vertices: v.co = J + R @ v.co
        b.data.update(); L.clean(b); return b
    # box faces: requested size, but each face either >= 1.6 mm outside the housing+servo+forearm hull (no thin slivers) - the volume between
    # the box and that hull is left solid (no thin air gaps), the hull itself is subtracted (keeps the servo pocket, forearm entry, housing)
    sv = L.imp(os.path.join(L.REF, f"s32_gripper_{s}.stl"), f"tmp_servo_{s}", TMP); fa = L.imp(os.path.join(L.REF, f"forearm_{s}.stl"), f"tmp_fa_{s}", TMP)
    Hl = [loc(v.co) for ob in (sv,) for v in ob.data.vertices] + [h for h in H if h[2] < top_d + 52]
    hx0, hx1 = min(h[0] for h in Hl) - J.x, max(h[0] for h in Hl) - J.x; ho0, ho1 = min(h[1] for h in Hl), max(h[1] for h in Hl); hd1 = max(loc(v.co)[2] for v in sv.data.vertices)
    BX = (min(-10.0 - J.x, hx0 - 1.6), max(19.0 - J.x, hx1 + 1.6), min(o_in + O0, ho0 - 1.6), max(o_in + O1, ho1 + 1.6, 48.5 + 1.8), top_d + float(os.environ.get("TOP_IN", 1.0)), max(top_d + float(os.environ.get('BOX_H', 48.0)), hd1 + 2.2))
    outer = lbox(f"tmp_outer_{s}", *BX, 3.0)
    DIRS = [Vector((i, j, k)).normalized() for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1) if (i, j, k) != (0, 0, 0)]
    def hull(name, obs, k, grow=0.0):
        if grow > 0:      # Minkowski of the plain hull's vertices with a 26-direction 'sphere' (offset >= 0.89*grow)
            h0 = hull(name + "_0", obs, 1.0); pts = [v.co.copy() for v in h0.data.vertices]
            obs = [type("P", (), {"data": type("D", (), {"vertices": [type("V", (), {"co": p + dd * grow})() for p in pts for dd in DIRS]})()})()]
        bm = bmesh.new()
        for ob in obs:
            for v in ob.data.vertices: bm.verts.new(v.co)
        bm.verts.ensure_lookup_table(); res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
        dv = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
        if dv: bmesh.ops.delete(bm, geom=dv, context="VERTS")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        ctr = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
        for v in bm.verts: v.co = ctr + (v.co - ctr) * k
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        h = bpy.data.objects.new(me.name, me); TMP.objects.link(h); return h
    # servo+horn+forearm hull x1.008 (clearance); housing hull x0.97 (box material overlaps ~0.4-1.3 mm into the housing walls -> fuses)
    L.boolean(outer, hull(f"tmp_hullA_{s}", (sv, hn, fa), 1.008), "DIFFERENCE")
    L.boolean(outer, hull(f"tmp_hullB_{s}", (hs0,), 0.97), "DIFFERENCE")
    # 3. minus the moving finger (+ horn) sweep: convex hull of the finger+horn copies at -14..64 deg (4 deg steps) about the gripper axis,
    #    scaled 1.04 about its centroid (~0.6-1 mm clearance); the swept fan is convex (<180 deg), so the hull ~ the swept volume
    bm = bmesh.new()
    for ang in range(-14, 65, 4):
        Mr = Matrix.Translation(J) @ Matrix.Rotation(math.radians(ang), 4, a) @ Matrix.Translation(-J)
        for src in (fm, hn):
            for v in src.data.vertices: bm.verts.new(Mr @ v.co)
    bm.verts.ensure_lookup_table(); res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    dv = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
    if dv: bmesh.ops.delete(bm, geom=dv, context="VERTS")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    ctr = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    for v in bm.verts: v.co = ctr + (v.co - ctr) * 1.04
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(f"tmp_sweep_{s}"); bm.to_mesh(me); bm.free(); sw = bpy.data.objects.new(me.name, me); TMP.objects.link(sw)
    L.boolean(outer, sw, "DIFFERENCE")
    # 3b. hollow the solid fill (mass): cavity = box inset WC minus the servo/forearm hull, the housing hull and the finger sweep, each grown
    #     by WC/0.89 -> >= WC (2.0 mm, ~4-5 perimeters) of material everywhere; enclosed voids, small cavity islands (<300 mm3) dropped
    WC = float(os.environ.get("WC", 0.0))   # hollowing tried (v3.32 h): only 3.9 cm3 of voids (fill is mostly <6 mm thick) -> off
    if WC > 0:
        g = WC / 0.89
        cav = lbox(f"tmp_cav_{s}", BX[0] + WC, BX[1] - WC, BX[2] + WC, BX[3] - WC, BX[4] + WC, BX[5] - WC, 1.0)
        for nm, obs in (("A", (sv, hn, fa)), ("B", (hs0,)), ("S", (sw,))): L.boolean(cav, hull(f"tmp_cg{nm}_{s}", obs, 1.0, g), "DIFFERENCE")
        L.clean(cav, 1e-3); cdrop = L.drop_islands(cav, 300.0)
        if len(cav.data.polygons): L.boolean(outer, cav, "DIFFERENCE")
        log.setdefault("cav", {})[s] = dict(dropped=[round(x, 1) for x in cdrop], faces=len(cav.data.polygons))
    # 4. union with the (stretched) housing
    L.boolean(hs, outer, "UNION"); L.clean(hs, 1e-3); drp = L.drop_islands(hs)
    log[s] = dict(drop=drp, DF=DF, O0=O0, O1=O1, o_in=round(o_in, 2), top_d=round(top_d, 2), box_local=[round(x, 2) for x in BX])
    es = L.imp(os.path.join(L.REF, f"elbow_sleeve_{s}.stl"), f"elbow_sleeve_{s}_v332_black", C)
for ob in list(TMP.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(TMP)
A = os.path.join(L.OUT, "asm"); P = os.path.join(L.OUT, "stl")
for s in "LR":
    L.export(bpy.data.objects[f"gripper_housing_{s}_v332"], os.path.join(A, f"gripper_housing_{s}.stl"))
    L.export(bpy.data.objects[f"finger_moving_{s}_v332"], os.path.join(A, f"finger_moving_{s}.stl"))
    L.export_print(bpy.data.objects[f"gripper_housing_{s}_v332"], os.path.join(P, f"v332_gripper_housing_{s}.stl"), f"gripper_housing_{s}")
    L.export_print(bpy.data.objects[f"finger_moving_{s}_v332"], os.path.join(P, f"v332_finger_moving_{s}.stl"), f"finger_moving_{s}")
mp_fn = os.path.join(A, "map.json"); mp = json.load(open(mp_fn)) if os.path.exists(mp_fn) else {}
for s in "LR": mp[f"gripper_housing_{s}"] = [f"fore_arm_{s}", "black"]; mp[f"finger_moving_{s}"] = [f"finger_{s}", "black"]
json.dump(mp, open(mp_fn, "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v332.blend"))
print("ARMS_DONE", json.dumps(log))
