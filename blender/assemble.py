# ROBOTZ.blend -> robo_master.blend : Head 2 + Body 5 + arms 5 + Head 4's spring antenna
import bpy, bmesh
D = bpy.data
HEAD, BODY, ARM, ANT_SRC = "geo_head_bot_1", "geo_body_bot_4", "geo_arm_bot_4", "geo_head_bot_3"

def loose_parts(bm):
    seen, parts = set(), []
    for v in bm.verts:
        if v in seen: continue
        stack, part = [v], []
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x); part.append(x); stack += [e.other_vert(x) for e in x.link_edges]
        parts.append(part)
    return parts

# antenna = Head 4's loose parts sitting above the head shell (spring + ball)
src = D.objects[ANT_SRC]
ant = src.copy(); ant.data = src.data.copy(); ant.name = ant.data.name = "geo_antenna"
bpy.context.scene.collection.objects.link(ant)
bm = bmesh.new(); bm.from_mesh(ant.data)
drop = [v for p in loose_parts(bm) if min(v.co.z for v in p) < 0.69 for v in p]
bmesh.ops.delete(bm, geom=drop, context='VERTS'); bm.to_mesh(ant.data); bm.free()
for m in [m for m in ant.modifiers if m.type == 'MASK']: ant.modifiers.remove(m)

# own bone for the antenna so it can spring independently
rig = D.objects["rig_bot"]
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
b = rig.data.edit_bones.new("Antenna_Spring")
b.head, b.tail = (0, 0, 0.70), (0, 0, 0.93)
b.parent = rig.data.edit_bones["DEF-Head"]
bpy.ops.object.mode_set(mode='OBJECT')
ant.vertex_groups.clear()
ant.vertex_groups.new(name="Antenna_Spring").add(range(len(ant.data.vertices)), 1.0, 'REPLACE')

# palette: tint white base textures (Multiply exports to glTF baseColorFactor)
PALETTE = {"mat_bot_1": (0.62, 0.72, 0.86), "mat_bot_4": (0.62, 0.72, 0.86), "mat_bot_3": (0.25, 0.85, 0.8)}  # gray-blue, teal
for name, rgb in PALETTE.items():
    nt = D.materials[name].node_tree
    bsdf = nt.nodes["Principled BSDF"]; tex = bsdf.inputs["Base Color"].links[0].from_socket
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs["Factor"].default_value = 1.0; mix.inputs[7].default_value = (*rgb, 1)
    nt.links.new(tex, mix.inputs[6]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])

keep = {"rig_bot", HEAD, BODY, ARM, "geo_antenna"}
for o in list(D.objects):
    if o.name not in keep: D.objects.remove(o)
for o in D.objects: o.hide_render = o.hide_viewport = False
bpy.ops.outliner.orphans_purge(do_recursive=True)
print("antenna verts:", len(ant.data.vertices))
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//../robo_master.blend"))
