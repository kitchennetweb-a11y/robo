# robo_master.blend -> ../robo.glb + ../face/*.png. Never saves the .blend.
import bpy, os
D = bpy.data
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "face"); os.makedirs(FACE, exist_ok=True)

# geometry: no subsurf, decimate the 48k-tri arms
for o in D.objects:
    for m in o.modifiers:
        if m.type == 'SUBSURF': m.show_viewport = m.show_render = False
arm = D.objects["geo_arm_bot_4"]
dec = arm.modifiers.new("Decimate", 'DECIMATE'); dec.ratio = 0.2
bpy.context.view_layer.objects.active = arm
bpy.ops.object.modifier_move_to_index(modifier="Decimate", index=0)

# face: dump every expression PNG for the web app, then make eye/mouth plain image materials (default face)
for g in D.node_groups:
    for n in g.nodes:
        if n.type == 'TEX_IMAGE' and n.image and n.image.name.startswith(("eye_", "mouth_")):
            n.image.save(filepath=os.path.join(FACE, n.image.name))
def face_mat(name, img):
    m = D.materials[name]; nt = m.node_tree; nt.nodes.clear()
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = D.images[img]
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"]); b.inputs["Emission Strength"].default_value = 1.0
    nt.links.new(b.outputs[0], o.inputs[0])
    if m.animation_data: m.node_tree.animation_data_clear()
face_mat("mat_bot_1_eye", "eye_normal_bot_1.png")
face_mat("mat_bot_mouth", "mouth_normal.png")

# body materials are solid: drop the pack's opacity maps so three.js doesn't treat them as transparent
for name in ("mat_bot_1", "mat_bot_3", "mat_bot_4"):
    a = D.materials[name].node_tree.nodes["Principled BSDF"].inputs["Alpha"]
    for l in list(a.links): D.materials[name].node_tree.links.remove(l)

# textures: 1k is plenty on an iPad screen
for img in D.images:
    if img.size[0] > 1024 and not img.name.startswith(("eye_", "mouth_")): img.scale(1024, 1024 * img.size[1] // img.size[0])

dg = bpy.context.evaluated_depsgraph_get(); total = 0
for o in D.objects:
    if o.type == 'MESH':
        me = o.evaluated_get(dg).to_mesh(); n = sum(len(p.vertices) - 2 for p in me.polygons); total += n
        print("TRIS", o.name, n)
print("TRIS total", total)

rig = D.objects["rig_bot"]; rig.animation_data.action = None
bpy.ops.export_scene.gltf(
    filepath=os.path.join(ROOT, "robo.glb"), export_format='GLB', export_apply=True,
    export_animations=True, export_animation_mode='ACTIONS', export_force_sampling=True,
    export_def_bones=True, export_anim_single_armature=True, export_reset_pose_bones=True,
    export_image_format='WEBP', export_draco_mesh_compression_enable=False, use_selection=False)
print("GLB", os.path.getsize(os.path.join(ROOT, "robo.glb")) // 1024, "KB")
