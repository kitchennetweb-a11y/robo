import bpy
L = []
for c in bpy.data.collections:
    L.append(f"COLL {c.name}: objs={[o.name for o in c.objects]} children={[k.name for k in c.children]}")
for o in bpy.data.objects:
    d = o.data
    extra = ""
    if o.type == 'MESH':
        extra = f" verts={len(d.vertices)} tris={sum(len(p.vertices)-2 for p in d.polygons)} mats={[m.name for m in d.materials if m]}"
        if d.shape_keys: extra += f" keys={[k.name for k in d.shape_keys.key_blocks]}"
        mods = [(m.type, getattr(m, 'object', None) and m.object.name) for m in o.modifiers]
        if mods: extra += f" mods={mods}"
        if o.vertex_groups: extra += f" vgroups={[g.name for g in o.vertex_groups][:12]}"
    if o.type == 'ARMATURE':
        extra = f" bones={[(b.name, b.parent.name if b.parent else None) for b in d.bones]}"
    loc = tuple(round(v, 3) for v in o.matrix_world.translation)
    L.append(f"OBJ {o.name} [{o.type}] parent={o.parent.name if o.parent else None} pbone={o.parent_bone or ''} loc={loc} dims={tuple(round(v,3) for v in o.dimensions)} hide={o.hide_render} colls={[c.name for c in o.users_collection]}{extra}")
for a in bpy.data.actions:
    L.append(f"ACTION {a.name} range={tuple(a.frame_range)} users={a.users}")
for m in bpy.data.materials:
    L.append(f"MAT {m.name}")
L.append(f"SCENES {[s.name for s in bpy.data.scenes]} engine={bpy.context.scene.render.engine}")
open(bpy.path.abspath("//../inventory.txt"), "w", encoding="utf-8").write("\n".join(L))
