# Find right-arm angles that bring Robo's hand (holding the cup) just in front of his mouth for the Drink pose.
# blender -b robo_master.blend -P drink_check.py   -> prints the best DRINK dict for animate.py
import bpy, math, itertools
from mathutils import Euler, Vector, Quaternion
s = bpy.context.scene; rig = bpy.data.objects["rig_bot"]; P = rig.pose.bones; head = bpy.data.objects["geo_head_bot_1"]
rig.animation_data.action = None
def qw(b, rx, ry, rz):
    r = P[b].bone.matrix_local.to_quaternion()
    return r.inverted() @ Euler([math.radians(a) for a in (rx, ry, rz)]).to_quaternion() @ r
slot = [i for i, m in enumerate(head.material_slots) if m.material and m.material.name == "mat_bot_mouth"][0]
def measure(out, fwd, elbow, twist, swing=0):
    for pb in P: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    P["Body"].rotation_quaternion = qw("Body", -5, 0, 0); P["Head"].rotation_quaternion = qw("Head", -18, 0, 0)  # drink lean + head back
    P["upper_arm_fk.R"].rotation_quaternion = qw("upper_arm_fk.R", -fwd, out, 0)
    P["forearm_fk.R"].rotation_quaternion = qw("forearm_fk.R", -elbow, swing, 0) @ Quaternion((0, 1, 0), math.radians(90 * twist))
    bpy.context.view_layer.update()
    me = head.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    vs = {i for p in me.polygons if p.material_index == slot for i in p.vertices}
    mouth = head.matrix_world @ (sum((me.vertices[i].co for i in vs), Vector()) / len(vs))
    pb = P["DEF-hand.R"]; hand = rig.matrix_world @ ((pb.head + pb.tail) / 2)
    target = mouth + Vector((0, -.07, -.03))  # cup rim at the mouth: hand a bit in front of and below it
    return (hand - target).length, hand - mouth
best = min(((measure(o, f, e, t, w)[0], (o, f, e, t, w)) for o, f, e, t, w in
            itertools.product([-20, 0, 15, 30], [80, 100, 120, 140], [20, 50, 80, 110], [0, .5], [-120, -90, -60, -30, 0])), key=lambda x: x[0])
err, (o, f, e, t, w) = best; d = measure(o, f, e, t, w)[1]
print(f"DRINK best out={o} fwd={f} elbow={e} twist={t} swing={w}  error {err:.3f} m  hand-mouth dx {d.x:+.3f} dy {d.y:+.3f} dz {d.z:+.3f}")
