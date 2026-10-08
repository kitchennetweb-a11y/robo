# Find right-arm angles for Drink: hand just in front of the mouth, palm facing sideways (toward the face's middle),
# thumb up — so the cup held in the palm stands upright. blender -b robo_master.blend -P drink_check.py
import bpy, math, itertools
from mathutils import Euler, Vector, Quaternion
s = bpy.context.scene; rig = bpy.data.objects["rig_bot"]; P = rig.pose.bones; head = bpy.data.objects["geo_head_bot_1"]
rig.animation_data.action = None
CURL = .45
def qw(b, rx, ry, rz):
    r = P[b].bone.matrix_local.to_quaternion()
    return r.inverted() @ Euler([math.radians(a) for a in (rx, ry, rz)]).to_quaternion() @ r
slot = [i for i, m in enumerate(head.material_slots) if m.material and m.material.name == "mat_bot_mouth"][0]
W = lambda v: rig.matrix_world @ v
def measure(out, fwd, elbow, swing, twist):
    for pb in P: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    P["Body"].rotation_quaternion = qw("Body", -5, 0, 0); P["Head"].rotation_quaternion = qw("Head", -18, 0, 0)
    P["upper_arm_fk.R"].rotation_quaternion = qw("upper_arm_fk.R", -fwd, out, 0)
    P["forearm_fk.R"].rotation_quaternion = qw("forearm_fk.R", -elbow, swing, 0) @ Quaternion((0, 1, 0), math.radians(90 * twist))
    for f in ("f_index", "f_middle", "f_pinky"):
        for k in ("01", "02", "03"): P[f"{f}.{k}.R"].rotation_quaternion = Euler((math.radians(85 * CURL), 0, 0)).to_quaternion()
    bpy.context.view_layer.update()
    me = head.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    vs = {i for p in me.polygons if p.material_index == slot for i in p.vertices}
    mouth = head.matrix_world @ (sum((me.vertices[i].co for i in vs), Vector()) / len(vs))
    h = P["DEF-hand.R"]; hand = W((h.head + h.tail) / 2)
    tips = sum((W(P[f"DEF-{f}.03.R"].tail) for f in ("f_index", "f_middle", "f_pinky")), Vector()) / 3
    palm = (tips - hand).normalized()                       # curled fingers point into the palm side
    thumb = (W(P["DEF-thumb.03.R"].tail) - hand).normalized()
    target = mouth + Vector((0, -.08, -.04))                # cup in front of / just below the mouth (robot faces -Y)
    score = (hand - target).length + .1 * palm.z ** 2 + .1 * (1 - max(thumb.z, 0)) + .05 * (1 - max(palm.x, 0))  # palm toward +x (middle)
    return score, hand - mouth, palm, thumb
grid = itertools.product([0, 15, 30, 45], [110, 130, 150, 170], [0, 20, 40, 60], [-60, -30, 0], [-1, -.5, 0, .5, 1])
best = min(((measure(*g)[0], g) for g in grid), key=lambda x: x[0])
score, g = best; _, d, palm, thumb = measure(*g)
print(f"DRINK best out={g[0]} fwd={g[1]} elbow={g[2]} swing={g[3]} twist={g[4]}  score {score:.3f}")
print(f"DRINK hand-mouth dx {d.x:+.3f} dy {d.y:+.3f} dz {d.z:+.3f}  palm {tuple(round(v, 2) for v in palm)}  thumb {tuple(round(v, 2) for v in thumb)}")
