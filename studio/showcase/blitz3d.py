"""Rotierender 3D-Blitz im Comic-Look (Blender, Cycles CPU, Freestyle).
Nutzung: blender -b -P blitz3d.py -- ausgabeordner/ [frames=90]
"""

import math
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1 :]
outdir = args[0]
frames = int(args[1]) if len(args) > 1 else 90

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# Blitz als 2D-Umriss, extrudiert
pts = [(-0.2, 1.6), (0.75, 1.6), (0.25, 0.35), (0.85, 0.35), (-0.45, -1.7), (-0.05, -0.2), (-0.65, -0.2)]
me = bpy.data.meshes.new("Blitz")
verts = [(x, 0, y) for x, y in pts]
me.from_pydata(verts, [], [list(range(len(pts)))])
ob = bpy.data.objects.new("Blitz", me)
sc.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0.35, 0)})
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
bev = ob.modifiers.new("Kante", "BEVEL")
bev.width = 0.04
bev.segments = 2
for v in ob.data.vertices:
    v.co.y -= 0.175

mat = bpy.data.materials.new("Toon")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
t = nt.nodes.new("ShaderNodeBsdfToon")
t.inputs["Color"].default_value = (1.0, 0.72, 0.0, 1)
t.inputs["Size"].default_value = 0.55
t.inputs["Smooth"].default_value = 0.02
g = nt.nodes.new("ShaderNodeBsdfToon")
g.component = "GLOSSY"
g.inputs["Size"].default_value = 0.12
g.inputs["Smooth"].default_value = 0.02
e = nt.nodes.new("ShaderNodeEmission")
e.inputs["Color"].default_value = (0.55, 0.3, 0.0, 1)
e.inputs["Strength"].default_value = 0.7
a1 = nt.nodes.new("ShaderNodeAddShader")
a2 = nt.nodes.new("ShaderNodeAddShader")
o = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(t.outputs[0], a1.inputs[0])
nt.links.new(g.outputs[0], a1.inputs[1])
nt.links.new(a1.outputs[0], a2.inputs[0])
nt.links.new(e.outputs[0], a2.inputs[1])
nt.links.new(a2.outputs[0], o.inputs[0])
ob.data.materials.append(mat)

# Drehung: eine volle Umdrehung, nahtlos
sc.frame_start, sc.frame_end = 1, frames
ob.rotation_euler = (0, 0, 0)
ob.keyframe_insert("rotation_euler", index=2, frame=1)
ob.rotation_euler = (0, 0, 2 * math.pi)
ob.keyframe_insert("rotation_euler", index=2, frame=frames + 1)
for fc in ob.animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"

bpy.ops.object.light_add(type="SUN")
sun = bpy.context.object
sun.data.energy = 3
sun.rotation_euler = (0.9, 0.3, -0.7)
bpy.ops.object.camera_add(location=(0, -6.5, 0), rotation=(math.pi / 2, 0, 0))
sc.camera = bpy.context.object
w = bpy.data.worlds.new("W")
w.color = (0.02, 0.02, 0.03)
sc.world = w

sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 12
sc.cycles.use_denoising = False
sc.render.resolution_x = sc.render.resolution_y = 720
sc.render.film_transparent = True
sc.render.use_freestyle = True
sc.render.line_thickness = 2.5
vl = sc.view_layers[0]
vl.use_freestyle = True
ls_style = bpy.data.linestyles.new("Tusche")
ls_style.color = (0.05, 0.03, 0.0)
if not vl.freestyle_settings.linesets:
    vl.freestyle_settings.linesets.new("L")
for ls in vl.freestyle_settings.linesets:
    ls.linestyle = ls_style
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.color_mode = "RGBA"
sc.render.filepath = outdir.rstrip("/") + "/f_"
bpy.ops.render.render(animation=True)
print("Fertig")
