# usage: blender -b robo_master.blend -P render_preview.py -- out_name [frame]
import bpy, sys, math, os
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
name = args[0] if args else "assembled"
s = bpy.context.scene
s.frame_set(int(args[1]) if len(args) > 1 else 1)
dg = bpy.context.evaluated_depsgraph_get()
pts = [o.matrix_world @ Vector(c) for o in s.objects if o.type == 'MESH' for c in o.evaluated_get(dg).bound_box]
lo = Vector(map(min, *pts)); hi = Vector(map(max, *pts)); c = (lo + hi) / 2; r = (hi - lo).length / 2
cam = bpy.data.objects.new("PrevCam", bpy.data.cameras.new("PrevCam")); s.collection.objects.link(cam)
cam.location = c + Vector((r * 1.2, -r * 3.2, r * 0.6))
cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
s.camera = cam
for i, (rot, e) in enumerate([((50, 0, 30), 4), ((60, 0, -120), 1.5)]):
    l = bpy.data.objects.new(f"L{i}", bpy.data.lights.new(f"L{i}", 'SUN')); s.collection.objects.link(l)
    l.rotation_euler = [math.radians(a) for a in rot]; l.data.energy = e
w = s.world or bpy.data.worlds.new("W"); s.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.88, 0.92, 1)
s.render.engine = 'BLENDER_EEVEE'
s.render.resolution_x, s.render.resolution_y = (int(args[2]),) * 2 if len(args) > 2 else (640, 800)  # 3rd arg: square size (icon)
s.render.image_settings.file_format = 'PNG'
s.render.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview", f"{name}.png")
bpy.ops.render.render(write_still=True)
