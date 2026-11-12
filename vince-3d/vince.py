"""Vince (maned wolf) — stylized base mesh built from an SDF, meshed with marching cubes.
Run: python vince.py [--views front,three_q,side,back,head] [--res 0.004] [--samples 48] [--expo -1.2]
(needs the `bpy`, `numpy`, `scikit-image` and `pillow` packages; see README.md)
Units: metres, Z up, character faces -Y.
"""
import os, sys, math, time
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix
from skimage.measure import marching_cubes

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(OUT, "renders"), exist_ok=True)
args = sys.argv[1:]
VOX = float(args[args.index("--res") + 1]) if "--res" in args else 0.004
VIEWS = (args[args.index("--views") + 1].split(",") if "--views" in args
         else ["front", "three_q", "side", "back", "head"])
EXPO = float(args[args.index("--expo") + 1]) if "--expo" in args else -1.2
SAMPLES = int(args[args.index("--samples") + 1]) if "--samples" in args else 48
t0 = time.time()

# ---------------------------------------------------------------- SDF primitives
def length(v): return np.sqrt(np.sum(v * v, axis=-1))

def sd_round_cone(p, a, b, r1, r2):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ba = b - a; l2 = ba @ ba; rr = r1 - r2; a2 = l2 - rr * rr; il2 = 1.0 / l2
    pa = p - a
    y = pa @ ba; z = y - l2
    q = pa * l2 - y[..., None] * ba
    x2 = np.sum(q * q, axis=-1)
    y2 = y * y * l2; z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    d = np.where(np.sign(y) * a2 * y2 < k, d2, d3)
    d = np.where(np.sign(z) * a2 * z2 > k, d1, d)
    t = np.clip(y * il2, 0, 1)
    return d, t

def rot(rx=0, ry=0, rz=0):
    return np.array(Matrix.Rotation(math.radians(rz), 3, 'Z') @ Matrix.Rotation(math.radians(ry), 3, 'Y')
                    @ Matrix.Rotation(math.radians(rx), 3, 'X'))

def sd_ellipsoid(p, c, r, R=None):
    q = p - np.asarray(c, float)
    if R is not None: q = q @ R          # world -> local (R orthonormal, row-vector form)
    r = np.asarray(r, float)
    k0 = length(q / r); k1 = length(q / (r * r))
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9), np.zeros(q.shape[:-1])

def smin(a, b, k):
    if k <= 0: return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25

# ---------------------------------------------------------------- body definition
PR = []   # (tag, kind, params, k, bbox_min, bbox_max)
def cone(tag, a, b, r1, r2, k=0.03):
    a = np.array(a, float); b = np.array(b, float); m = max(r1, r2) + k
    PR.append((tag, 'cone', (a, b, r1, r2), k, np.minimum(a, b) - m, np.maximum(a, b) + m))
def ell(tag, c, r, k=0.03, R=None):
    c = np.array(c, float); m = max(r) + k
    PR.append((tag, 'ell', (c, r, R), k, c - m, c + m))
def chain(tag, pts, rads, k=0.03):
    for i in range(len(pts) - 1):
        cone(f"{tag}{i}", pts[i], pts[i + 1], rads[i], rads[i + 1], k)

def sym(fn):  # build left (+x) and right (-x)
    for s in (1, -1): fn(s, "L" if s > 0 else "R")

# torso
ell("chest", (0, 0.0, 1.37), (0.172, 0.118, 0.15), k=0.07)
ell("ribs", (0, 0.01, 1.25), (0.135, 0.103, 0.12), k=0.07)
ell("waist", (0, 0.012, 1.13), (0.105, 0.085, 0.10), k=0.07)
ell("pelvis", (0, 0.018, 1.00), (0.118, 0.09, 0.09), k=0.06)
cone("neck", (0, 0.012, 1.46), (0, -0.005, 1.66), 0.07, 0.055, k=0.05)
def shoulders(s, n):
    ell("shoulder" + n, (s * 0.185, 0.012, 1.445), (0.072, 0.07, 0.062), k=0.06)
    ell("glute" + n, (s * 0.06, 0.05, 0.975), (0.065, 0.065, 0.078), k=0.05)
sym(shoulders)

# head
ell("cranium", (0, 0.0, 1.73), (0.098, 0.105, 0.094), k=0.04)
ell("brow", (0, -0.05, 1.742), (0.075, 0.055, 0.052), k=0.04)
cone("muzzle", (0, -0.065, 1.705), (0, -0.245, 1.68), 0.05, 0.022, k=0.04)
cone("jaw", (0, -0.045, 1.665), (0, -0.205, 1.658), 0.043, 0.016, k=0.03)
ell("nose", (0, -0.25, 1.686), (0.017, 0.014, 0.013), k=0.012)
def cheeks(s, n):
    ell("cheek" + n, (s * 0.062, -0.035, 1.67), (0.055, 0.055, 0.045), k=0.04)
    for (dx, dy, dz) in [(0.045, 0.015, -0.02), (0.035, 0.025, -0.05)]:
        cone("cheekfluff" + n, (s * 0.085, -0.02, 1.665), (s * (0.085 + dx), -0.02 + dy, 1.665 + dz), 0.026, 0.004, k=0.015)
sym(cheeks)
# head tuft (dark), swept back
# dark fringe falling forward between the ears
for (x, a, b) in [(0.0, (0, 0.03, 1.81), (0, -0.075, 1.80)), (0.018, (0.018, 0.04, 1.81), (0.03, -0.055, 1.79)),
                  (-0.018, (-0.018, 0.04, 1.81), (-0.03, -0.055, 1.79)), (0, (0, 0.06, 1.80), (0, -0.01, 1.835))]:
    cone("tuft", a, b, 0.026, 0.004, k=0.02)
# mane crest down the back of the neck
for i, z in enumerate(np.linspace(1.70, 1.44, 5)):
    y = 0.07 + 0.02 * (1.70 - z) / 0.26
    cone("mane", (0, y - 0.035, z), (0, y + 0.022, z + 0.04), 0.036, 0.008, k=0.03)
# chest ruff
for (x, z) in [(0, 1.50), (0.05, 1.52), (-0.05, 1.52), (0.025, 1.47), (-0.025, 1.47)]:
    cone("ruff", (x, -0.03, z + 0.03), (x * 1.3, -0.105, z - 0.04), 0.035, 0.004, k=0.02)

# legs (digitigrade)
LEG = {}
def leg(s, n):
    hip, knee, hock, ball, toe = ((s * 0.088, 0.015, 0.97), (s * 0.11, -0.075, 0.585),
                                  (s * 0.115, 0.10, 0.22), (s * 0.115, -0.045, 0.045), (s * 0.115, -0.10, 0.025))
    LEG[n] = (hip, knee, hock, ball)
    cone("thigh" + n, hip, knee, 0.085, 0.05, k=0.05)
    cone("shin" + n, knee, hock, 0.048, 0.031, k=0.03)
    cone("meta" + n, hock, ball, 0.031, 0.034, k=0.025)
    ell("foot" + n, (s * 0.115, -0.065, 0.032), (0.047, 0.055, 0.03), k=0.025)
    for i, dx in enumerate((-0.03, -0.01, 0.01, 0.03)):
        cone("toe" + n, (s * 0.115 + dx, -0.075, 0.03), (s * 0.115 + dx * 1.15, -0.112 + abs(dx) * 0.4, 0.018), 0.016, 0.013, k=0.008)
    for (dx, dz) in [(0.06, 0.0), (0.05, -0.04)]:  # elbow-ish fluff at hock
        cone("hockfluff" + n, (s * 0.115, 0.10, 0.22 + dz), (s * 0.115, 0.10 + dx, 0.20 + dz), 0.025, 0.004, k=0.012)
sym(leg)

# arms (relaxed A-pose)
ARM = {}
def arm(s, n):
    sh, el, wr = (s * 0.19, 0.012, 1.43), (s * 0.30, 0.045, 1.17), (s * 0.375, -0.005, 0.945)
    ARM[n] = (sh, el, wr)
    cone("uparm" + n, sh, el, 0.048, 0.037, k=0.04)
    cone("forearm" + n, el, wr, 0.037, 0.027, k=0.03)
    cone("elbowfluff" + n, (s * 0.30, 0.04, 1.17), (s * 0.325, 0.10, 1.13), 0.022, 0.004, k=0.012)
    ell("palm" + n, (s * 0.39, -0.008, 0.895), (0.022, 0.042, 0.05), k=0.025, R=rot(0, s * 12, 0))
    for i, dy in enumerate((-0.027, -0.009, 0.009, 0.027)):
        base = np.array((s * 0.397, -0.008 + dy, 0.86))
        mid = base + np.array((s * 0.008, dy * 0.15 - 0.012, -0.045 + abs(dy) * 0.4))
        tip = mid + np.array((-s * 0.004, -0.018, -0.022))
        cone("finger" + n, base, mid, 0.0125, 0.0105, k=0.006)
        cone("finger" + n, mid, tip, 0.0105, 0.009, k=0.004)
    cone("thumb" + n, (s * 0.385, -0.04, 0.905), (s * 0.375, -0.07, 0.87), 0.013, 0.010, k=0.008)
sym(arm)

# tail — bushy, hangs down and slightly to the side (+x), white tip
TAIL = [(0, 0.085, 1.0), (0.02, 0.18, 0.92), (0.06, 0.27, 0.74), (0.09, 0.29, 0.55), (0.105, 0.27, 0.40), (0.11, 0.24, 0.31)]
chain("tail", TAIL, [0.035, 0.07, 0.09, 0.085, 0.06, 0.012], k=0.03)
for i in range(1, 5):  # fluff spikes along the tail
    a = np.array(TAIL[i]); b = np.array(TAIL[i + 1]); d = (b - a)
    for ang in (0, 120, 240):
        off = np.array((math.cos(math.radians(ang)), 0.3, math.sin(math.radians(ang)))) * 0.06
        cone(f"tailfluff{i}", a + d * 0.5, a + d * 0.9 + off, 0.04, 0.004, k=0.025)

print(f"primitives: {len(PR)}")

# ---------------------------------------------------------------- evaluate on grid
def eval_prim(pr, P):
    tag, kind, par, k, lo, hi = pr
    if kind == 'cone': return sd_round_cone(P, *par)
    return sd_ellipsoid(P, *par)

lo = np.min([p[4] for p in PR], axis=0) - 0.02
hi = np.max([p[5] for p in PR], axis=0) + 0.02
shape = np.ceil((hi - lo) / VOX).astype(int) + 1
print("grid", shape, "voxels", np.prod(shape))
F = np.full(shape, 1.0, np.float32)
axes = [lo[i] + np.arange(shape[i]) * VOX for i in range(3)]
for pr in PR:
    i0 = np.clip(np.floor((pr[4] - lo) / VOX).astype(int), 0, shape - 1)
    i1 = np.clip(np.ceil((pr[5] - lo) / VOX).astype(int) + 1, 0, shape)
    X, Y, Z = np.meshgrid(axes[0][i0[0]:i1[0]], axes[1][i0[1]:i1[1]], axes[2][i0[2]:i1[2]], indexing='ij')
    P = np.stack([X, Y, Z], -1)
    d, _ = eval_prim(pr, P)
    blk = F[i0[0]:i1[0], i0[1]:i1[1], i0[2]:i1[2]]
    F[i0[0]:i1[0], i0[1]:i1[1], i0[2]:i1[2]] = smin(blk, d.astype(np.float32), pr[3])
print(f"field done {time.time()-t0:.1f}s")
verts, faces, normals, _ = marching_cubes(F, 0.0, spacing=(VOX, VOX, VOX))
verts += lo
print(f"mesh: {len(verts)} verts {len(faces)} faces {time.time()-t0:.1f}s")

def field_at(pts):
    pts = np.atleast_2d(np.asarray(pts, float)); f = np.full(len(pts), 1.0)
    for pr in PR: f = smin(f, eval_prim(pr, pts)[0], pr[3])
    return f

def surface_along(start, direction, max_d=0.3):
    """march from a point inside the body along direction until leaving the surface"""
    start = np.array(start, float); d = np.array(direction, float); d /= np.linalg.norm(d)
    ts = np.linspace(0, max_d, 1500); f = field_at(start + ts[:, None] * d)
    i = np.argmax(f > 0); return start + ts[i] * d

# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def hexlin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)

def material(name, hexc, rough=0.7, sheen=0.08, metal=0.0, spec=0.3):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexlin(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for nm, v in (("Sheen Weight", sheen), ("Specular IOR Level", spec)):
        if nm in b.inputs: b.inputs[nm].default_value = v
    return m

PAL = {"gold": "#C8892B", "cream": "#ECE3CF", "black": "#1A1A16", "amber": "#D99A2B"}
M = {
    "gold": material("Fur_CopperGold", PAL["gold"]),
    "cream": material("Fur_Cream", PAL["cream"]),
    "black": material("Fur_JetBlack", PAL["black"], rough=0.85),
    "brown": material("Fur_DarkBrown", "#3A2618", rough=0.85),
    "nose": material("Nose", "#141210", rough=0.35, sheen=0, spec=0.5),
    "claw": material("Claw", "#3B3A38", rough=0.4, sheen=0),
    "sclera": material("Eye_Sclera", "#F2EEE4", rough=0.2, sheen=0),
    "iris": material("Eye_Iris_Amber", PAL["amber"], rough=0.15, sheen=0),
    "pupil": material("Eye_Pupil", "#050505", rough=0.1, sheen=0),
    "steel": material("Glasses_SteelGraphite", "#4A4D52", rough=0.3, metal=1.0, sheen=0),
    "hoop": material("Earring_MatteBlack", "#121212", rough=0.6, sheen=0),
    "lens": None,
}
lens = bpy.data.materials.new("Glasses_Lens"); lens.use_nodes = True
lb = lens.node_tree.nodes["Principled BSDF"]
lb.inputs["Base Color"].default_value = (0.9, 0.95, 1, 1); lb.inputs["Roughness"].default_value = 0.0
if "Transmission Weight" in lb.inputs: lb.inputs["Transmission Weight"].default_value = 1.0
lb.inputs["Alpha"].default_value = 0.15
M["lens"] = lens
ORDER = ["gold", "cream", "black", "brown", "nose"]

# body mesh
me = bpy.data.meshes.new("Vince_Body")
me.from_pydata(verts.tolist(), [], faces[:, ::-1].tolist() if False else faces.tolist())
me.update()
body = bpy.data.objects.new("Vince_Body", me); sc.collection.objects.link(body)
for k in ORDER: me.materials.append(M[k])
# fix normals outward
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
me.shade_smooth() if hasattr(me, "shade_smooth") else None
for p in me.polygons: p.use_smooth = True

# ---------------------------------------------------------------- colour zones
nf = len(me.polygons)
C = np.zeros(nf * 3); me.polygons.foreach_get("center", C); C = C.reshape(-1, 3)
N = np.zeros(nf * 3); me.polygons.foreach_get("normal", N); N = N.reshape(-1, 3)
best = np.full(nf, 9.0); tag = np.empty(nf, dtype=object); tpar = np.zeros(nf)
for pr in PR:
    sel = np.all((C >= pr[4]) & (C <= pr[5]), axis=1)
    if not sel.any(): continue
    d, t = eval_prim(pr, C[sel])
    idx = np.where(sel)[0]; better = d < best[idx]
    best[idx[better]] = d[better]; tag[idx[better]] = pr[0]; tpar[idx[better]] = t[better]
tag = np.array([str(t) for t in tag])
x, y, z = C[:, 0], C[:, 1], C[:, 2]; ax = np.abs(x)
ny, nz = N[:, 1], N[:, 2]
col = np.array(["gold"] * nf, dtype=object)
def has(prefix): return np.char.startswith(tag.astype(str), prefix)

# lower limbs: jet black, sharp cut
col[has("shin") | has("meta") | has("foot") | has("toe") | has("hockfluff")] = "black"
col[has("thigh") & (z < 0.70)] = "black"
col[has("forearm") | has("palm") | has("finger") | has("thumb")] = "black"
col[has("uparm") & (z < 1.25)] = "black"
col[has("elbowfluff")] = "black"
# front cream band (throat -> groin), width tapers
w = np.interp(z, [0.86, 0.95, 1.10, 1.25, 1.42, 1.60], [0.05, 0.075, 0.075, 0.115, 0.125, 0.06])
front = (ny < -0.2) & (ax < w)
torso = has("chest") | has("ribs") | has("waist") | has("pelvis") | has("neck") | has("ruff") | has("glute") | has("shoulder")
col[torso & front] = "cream"
col[has("ruff")] = "cream"
# inner thigh cream
col[has("thigh") & (z > 0.70) & (z < 0.95) & (np.sign(x) * N[:, 0] < -0.3)] = "cream"
# dark V across the upper chest
zv = 1.36 + 0.55 * ax
col[torso & (ny < -0.1) & (np.abs(z - zv) < 0.022) & (ax < 0.17)] = "brown"
# dark mane: back of head, neck, spine
back = (ny > 0.25)
spine_w = np.interp(z, [1.0, 1.2, 1.4, 1.5, 1.75], [0.03, 0.06, 0.10, 0.07, 0.05])
col[(torso | has("cranium")) & back & (ax < spine_w) & (z > 0.98)] = "black"
col[has("mane") | has("tuft")] = "black"
# head
head = has("cranium") | has("brow") | has("cheek") | has("muzzle") | has("jaw")
col[has("cheekfluff")] = "cream"
col[has("cheek") & ((z < 1.685) | (ny < -0.5))] = "cream"
col[has("jaw")] = "cream"
mz = np.interp(-y, [0.065, 0.245], [1.705, 1.68])
col[has("muzzle") & (z < mz - 0.012) & (nz < 0.4)] = "cream"
col[has("neck") & (ny < -0.1)] = "cream"
col[has("nose")] = "nose"
col[has("muzzle") & (y < -0.238) & (z > 1.674)] = "nose"
# tail: copper with a dark saddle at the root, cream tip
col[has("tail0") | ((has("tail1")) & (nz > 0.3))] = "black"
col[has("tail4") | has("tail3") & (tpar > 0.55)] = "cream"
col[has("tailfluff4")] = "cream"
mi = np.array([ORDER.index(c) for c in col], dtype=np.int32)
me.polygons.foreach_set("material_index", mi)
me.update()
print(f"coloured {time.time()-t0:.1f}s")

# light smoothing to remove voxel stepping
mod = body.modifiers.new("Smooth", 'CORRECTIVE_SMOOTH'); mod.iterations = 4; mod.smooth_type = 'SIMPLE'; mod.use_only_smooth = True
try: mod.rest_source = 'ORCO'
except Exception: pass

# ---------------------------------------------------------------- accessories / details
def obj_from_bm(name, bm_, mat_list):
    m = bpy.data.meshes.new(name); bm_.to_mesh(m); bm_.free()
    o = bpy.data.objects.new(name, m); sc.collection.objects.link(o)
    for mt in mat_list: m.materials.append(mt)
    for p in m.polygons: p.use_smooth = True
    return o

def cone_between(name, a, b, r1, r2, mat, segs=12):
    a = Vector(a); b = Vector(b); d = b - a
    bm_ = bmesh.new()
    bmesh.ops.create_cone(bm_, cap_ends=True, segments=segs, radius1=r1, radius2=r2, depth=d.length)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bmesh.ops.transform(bm_, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4(), verts=bm_.verts)
    return obj_from_bm(name, bm_, [mat])

def sphere(name, c, r, mat, scale=(1, 1, 1), segs=32):
    bm_ = bmesh.new(); bmesh.ops.create_uvsphere(bm_, u_segments=segs, v_segments=segs // 2, radius=r)
    bmesh.ops.scale(bm_, vec=scale, verts=bm_.verts)
    bmesh.ops.translate(bm_, vec=Vector(c), verts=bm_.verts)
    return obj_from_bm(name, bm_, [mat])

# claws: fingers and toes
for n, s in (("L", 1), ("R", -1)):
    for dy in (-0.027, -0.009, 0.009, 0.027):
        base = np.array((s * 0.397, -0.008 + dy, 0.86))
        mid = base + np.array((s * 0.008, dy * 0.15 - 0.012, -0.045 + abs(dy) * 0.4))
        tip = mid + np.array((-s * 0.004, -0.018, -0.022))
        dirv = (tip - mid) / np.linalg.norm(tip - mid)
        cone_between("Claw_hand" + n, tip - dirv * 0.004, tip + dirv * 0.03 + np.array((0, -0.01, 0)), 0.0075, 0.0008, M["claw"])
    cone_between("Claw_thumb" + n, (s * 0.375, -0.07, 0.87), (s * 0.372, -0.095, 0.855), 0.0075, 0.0008, M["claw"])
    for dx in (-0.03, -0.01, 0.01, 0.03):
        tip = np.array((s * 0.115 + dx * 1.15, -0.112 + abs(dx) * 0.4, 0.018))
        cone_between("Claw_foot" + n, tip + np.array((0, 0.006, 0)), tip + np.array((0, -0.03, -0.012)), 0.008, 0.0008, M["claw"])

# eyes
EYE = {}
for n, s in (("L", 1), ("R", -1)):
    inside = np.array((s * 0.038, -0.03, 1.735))
    d = np.array((s * 0.45, -1.0, 0.05))
    surf = surface_along(inside, d)
    dn = d / np.linalg.norm(d)
    c = surf - dn * 0.009
    EYE[n] = (surf, dn)
    e = sphere("Eye_" + n, c, 0.02, M["sclera"], scale=(1, 1, 0.75))
    sphere("Iris_" + n, c + dn * 0.0115, 0.0115, M["iris"], scale=(1, 1, 1.0))
    sphere("Pupil_" + n, c + dn * 0.0165, 0.0058, M["pupil"], scale=(1, 1, 1.15))

# ears: big maned-wolf ears with cream inner fluff, plus 3 matte-black hoops each
def ear(n, s):
    base = np.array((s * 0.06, 0.02, 1.785))
    tilt = Matrix.Rotation(math.radians(s * 14), 4, 'Z') @ Matrix.Rotation(math.radians(s * 17), 4, 'Y') @ Matrix.Rotation(math.radians(-6), 4, 'X')
    H = 0.19
    for part, (r, sy, off, mat) in {"outer": (0.06, 0.32, 0.0, M["gold"]), "inner": (0.045, 0.22, -0.012, M["cream"])}.items():
        bm_ = bmesh.new()
        bmesh.ops.create_cone(bm_, cap_ends=True, segments=24, radius1=r, radius2=0.002, depth=H * (1 if part == "outer" else 0.86))
        bmesh.ops.scale(bm_, vec=(1, sy, 1), verts=bm_.verts)
        bmesh.ops.translate(bm_, vec=Vector((0, off, H / 2 * (1 if part == "outer" else 0.86))), verts=bm_.verts)
        bmesh.ops.transform(bm_, matrix=Matrix.Translation(Vector(base)) @ tilt, verts=bm_.verts)
        o = obj_from_bm(f"Ear_{part}_{n}", bm_, [mat])
        o.modifiers.new("sub", 'SUBSURF').levels = 1
    # hoops along the outer rim
    for i, hz in enumerate((0.035, 0.06, 0.085)):
        rim = Vector((s * (0.06 * (1 - hz / H) - 0.002), 0, hz))
        p = Matrix.Translation(Vector(base)) @ tilt @ rim
        bm_ = bmesh.new()
        bm_t = bpy.data.meshes.new("tmp")
        bpy.ops.mesh.primitive_torus_add(major_radius=0.0075, minor_radius=0.0015, major_segments=24, minor_segments=8,
                                         location=p, rotation=(math.radians(90), 0, math.radians(s * 14)))
        h = bpy.context.object; h.name = f"Earring_{n}{i}"; h.data.materials.append(M["hoop"])
        bm_.free(); bpy.data.meshes.remove(bm_t)
sym(lambda s, n: ear(n, s))

# glasses: geometric steel-graphite frames
def glasses():
    eL, dL = EYE["L"]; eR, dR = EYE["R"]
    zc = (eL[2] + eR[2]) / 2 - 0.003
    yc = min(eL[1], eR[1]) - 0.03
    cu = bpy.data.curves.new("Glasses", 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 0.0022; cu.bevel_resolution = 3
    W, Hh, ch = 0.026, 0.019, 0.007  # half-width, half-height, chamfer (geometric lens)
    for s in (1, -1):
        cx = s * (abs(eL[0]) - 0.004)
        pts = [(-W + ch, -Hh), (W - ch, -Hh), (W, -Hh + ch), (W, Hh - ch * 0.4), (W - ch, Hh), (-W + ch, Hh), (-W, Hh - ch), (-W, -Hh + ch)]
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1); sp.use_cyclic_u = True
        for i, (u, v) in enumerate(pts):
            yy = yc + (s * u) * 0.35 * (1 if (s * u) > 0 else 0.15)   # wrap toward the sides
            sp.points[i].co = (cx + u, yy, zc + v, 1)
        # temple arm back to the ear
        sp = cu.splines.new('POLY'); sp.points.add(2)
        sp.points[0].co = (cx + s * W, yc + W * 0.35, zc + Hh - ch, 1)
        sp.points[1].co = (s * 0.083, yc + 0.06, zc + 0.008, 1)
        sp.points[2].co = (s * 0.09, 0.02, zc + 0.012, 1)
    sp = cu.splines.new('POLY'); sp.points.add(2)      # bridge
    sp.points[0].co = (0.042 - W, yc, zc + 0.006, 1); sp.points[1].co = (0, yc - 0.006, zc + 0.012, 1)
    sp.points[2].co = (-0.042 + W, yc, zc + 0.006, 1)
    o = bpy.data.objects.new("Glasses", cu); sc.collection.objects.link(o); cu.materials.append(M["steel"])
glasses()
print(f"accessories {time.time()-t0:.1f}s")

# ---------------------------------------------------------------- lighting, cameras, render
w = bpy.data.worlds.new("World"); sc.world = w
try: w.use_nodes = True
except Exception: pass
w.node_tree.nodes["Background"].inputs[0].default_value = hexlin("#24364F")
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
def light(name, kind, loc, energy, size=1.0, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, kind); l.energy = energy; l.color = color
    if kind == 'AREA': l.size = size
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1.2)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
light("Key", 'AREA', (-1.6, -2.2, 2.6), 420, 1.5, (1, 0.96, 0.9))
light("Fill", 'AREA', (2.2, -1.5, 1.4), 140, 2.0, (0.85, 0.9, 1))
light("Rim", 'AREA', (0.8, 2.4, 2.4), 450, 1.2, (0.9, 0.95, 1))
# floor
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1.2, fill_type='NGON', location=(0, 0, 0))
fl = bpy.context.object; fl.name = "Floor"; fl.data.materials.append(material("Floor", "#1C2838", rough=0.9, sheen=0))

sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.render.film_transparent = False
vts = [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items]
sc.view_settings.view_transform = 'Khronos PBR Neutral' if 'Khronos PBR Neutral' in vts else 'Standard'
sc.view_settings.look = 'None'
sc.view_settings.exposure = EXPO

CAMS = {  # name: (location, target, lens, resolution)
    "front": ((0, -6.0, 1.0), (0, 0, 0.98), 75, (700, 1000)),
    "three_q": ((-3.9, -4.6, 1.15), (0, 0.02, 0.98), 75, (700, 1000)),
    "side": ((6.0, 0.02, 1.0), (0, 0.02, 0.98), 75, (700, 1000)),
    "back": ((1.2, 5.9, 1.1), (0, 0, 0.98), 75, (700, 1000)),
    "head": ((-0.55, -0.85, 1.80), (0, -0.07, 1.71), 85, (800, 800)),
}
files = []
for v in VIEWS:
    loc, tgt, lensmm, res = CAMS[v]
    cd = bpy.data.cameras.new(v); cd.lens = lensmm
    co = bpy.data.objects.new("Cam_" + v, cd); sc.collection.objects.link(co); co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co; sc.render.resolution_x, sc.render.resolution_y = res
    fp = os.path.join(OUT, "renders", f"render_{v}.png"); sc.render.filepath = fp
    bpy.ops.render.render(write_still=True); files.append(fp)
    print(f"rendered {v} {time.time()-t0:.1f}s")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "vince.blend"))
for o in list(sc.objects):
    o.select_set(o.type in ('MESH', 'CURVE') and o.name != "Floor")
try:
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "vince.glb"), use_selection=True, export_apply=True)
except Exception as ex: print("GLB export failed", ex)
# contact sheet
from PIL import Image
ims = [Image.open(f) for f in files if "head" not in f]
if ims:
    W_ = sum(i.width for i in ims); H_ = max(i.height for i in ims)
    sheet = Image.new("RGB", (W_, H_)); xo = 0
    for i in ims: sheet.paste(i, (xo, 0)); xo += i.width
    sheet.save(os.path.join(OUT, "renders", "sheet.png"))
print(f"done {time.time()-t0:.1f}s")
