# close-ups of the hand in the real actions, front view
import bpy, math, os
import numpy as np
from mathutils import Vector
D = bpy.data; s = bpy.context.scene; rig = D.objects["rig_bot"]; P = rig.pose.bones
cam = D.objects.new("C", D.cameras.new("C")); s.collection.objects.link(cam); s.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = .3; cam.rotation_euler = (math.radians(90), 0, 0)
l = D.objects.new("L", D.lights.new("L", 'SUN')); s.collection.objects.link(l); l.rotation_euler = (math.radians(60), 0, math.radians(20)); l.data.energy = 4
s.world.use_nodes = True; s.world.node_tree.nodes["Background"].inputs[0].default_value = (.85, .88, .92, 1)
s.render.engine = 'BLENDER_EEVEE'; s.render.resolution_x = s.render.resolution_y = 260; s.render.image_settings.file_format = 'PNG'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview"); cells = []
for act, fr, side in (("Wave", 18, "L"), ("Wave", 26, "L"), ("ThumbsUp", 30, "R"), ("ThumbsUp", 37, "R")):
    rig.animation_data.action = D.actions[act]; s.frame_set(fr)
    cam.location = rig.matrix_world @ P[f"DEF-hand.{side}"].head + Vector((0, -2, 0))
    p = os.path.join(OUT, "_h.png"); s.render.filepath = p; bpy.ops.render.render(write_still=True)
    im = D.images.load(p); cells.append(np.array(im.pixels[:]).reshape(260, 260, 4)); D.images.remove(im)
sh = np.hstack(cells).astype(np.float32)
im = D.images.new("h", sh.shape[1], sh.shape[0]); im.pixels.foreach_set(sh.ravel())
im.filepath_raw = os.path.join(OUT, "hands.png"); im.file_format = 'PNG'; im.save(); os.remove(p)
