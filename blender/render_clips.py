# usage: blender -b robo_master.blend -P render_clips.py [-- Clip1 Clip2 ...]
# renders 4 frames per action into contact sheets preview/clips_N.png (6 clips per sheet)
import bpy, sys, os, math
import numpy as np
from mathutils import Vector
want = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
s = bpy.context.scene; rig = bpy.data.objects["rig_bot"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")
W, H, COLS = 240, 300, (.1, .35, .6, .95)

cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); s.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.9
tgt = Vector((0, 0, .65)); cam.location = tgt + Vector((.35, -1, .25)).normalized() * 6
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler(); s.camera = cam
for i, (rot, e) in enumerate([((50, 0, 30), 4), ((60, 0, -120), 1.5)]):
    l = bpy.data.objects.new(f"L{i}", bpy.data.lights.new(f"L{i}", 'SUN')); s.collection.objects.link(l)
    l.rotation_euler = [math.radians(a) for a in rot]; l.data.energy = e
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
w = s.world or bpy.data.worlds.new("W"); s.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (.85, .88, .92, 1)
s.render.engine = 'BLENDER_EEVEE'; s.render.resolution_x, s.render.resolution_y = W, H
s.render.image_settings.file_format = 'PNG'

acts = [a for a in bpy.data.actions if not want or a.name in want]
rows = []
for a in acts:
    rig.animation_data.action = a; f0, f1 = a.frame_range; cells = []
    for c in COLS:
        s.frame_set(round(f0 + c * (f1 - f0)))
        p = os.path.join(OUT, "_tmp.png"); s.render.filepath = p; bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(p); px = np.array(img.pixels[:]).reshape(H, W, 4); bpy.data.images.remove(img)
        px[:3, :, :3] = .4  # cell separator
        cells.append(px)
    rows.append((a.name, np.hstack(cells)))
    print("RENDERED", a.name)
for k in range(0, len(rows), 6):
    chunk = rows[k:k + 6]; sheet = np.vstack([r for _, r in reversed(chunk)])  # pixels are bottom-up
    im = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0]); im.pixels.foreach_set(sheet.astype(np.float32).ravel())
    im.filepath_raw = os.path.join(OUT, f"clips_{k // 6 + 1}.png"); im.file_format = 'PNG'; im.save()
    print("SHEET", k // 6 + 1, [n for n, _ in chunk])
os.remove(os.path.join(OUT, "_tmp.png"))
