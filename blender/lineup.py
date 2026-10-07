# render each head/body/arm variant side by side, labelled by index (x offset = index)
import bpy
D = bpy.data
for o in list(D.objects):
    if not o.name.startswith(("geo_head_bot_", "geo_body_bot_", "geo_arm_bot_", "rig_bot")) or "deformer" in o.name:
        D.objects.remove(o)
for o in list(D.objects):
    if o.type != 'MESH': continue
    kind, i = o.name.split("_")[1], int(o.name[-1])
    c = o.copy(); bpy.context.scene.collection.objects.link(c)
    c.parent = None; c.modifiers.remove(c.modifiers["Armature"]) if "Armature" in c.modifiers else None
    c.location = (i * 0.8, 0, {"head": 0, "body": -0.9, "arm": -1.8}[kind])
    c.hide_render = False
    D.objects.remove(o)
D.objects.remove(D.objects["rig_bot"])
