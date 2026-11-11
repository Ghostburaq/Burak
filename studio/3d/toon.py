"""3D-Szene im Comic-/Manga-Look rendern (Blender headless, Toon-Shading + Konturlinien).

Nutzung: blender -b -P toon.py -- ausgabe.png [modell.glb|.obj|.fbx]
Ohne Modell wird eine Demo-Figur (Suzanne) gerendert.
"""

import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
out = args[0] if args else "/tmp/toon.png"
model = args[1] if len(args) > 1 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

if model:
    ext = model.lower().rsplit(".", 1)[-1]
    {
        "glb": bpy.ops.import_scene.gltf,
        "gltf": bpy.ops.import_scene.gltf,
        "obj": bpy.ops.wm.obj_import,
        "fbx": bpy.ops.import_scene.fbx,
    }[ext](filepath=model)
    objs = [o for o in scene.objects if o.type == "MESH"]
else:
    bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
    obj = bpy.context.object
    obj.modifiers.new("glatt", "SUBSURF").levels = 2
    bpy.ops.object.shade_smooth()
    objs = [obj]

# Toon-Material (Cycles Toon BSDF): harte Licht-/Schattenkante + Glanzpunkt
mat = bpy.data.materials.new("Toon")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
toon = nt.nodes.new("ShaderNodeBsdfToon")
toon.inputs["Color"].default_value = (1.0, 0.55, 0.2, 1)
toon.inputs["Size"].default_value = 0.6
toon.inputs["Smooth"].default_value = 0.02
gloss = nt.nodes.new("ShaderNodeBsdfToon")
gloss.component = "GLOSSY"
gloss.inputs["Size"].default_value = 0.15
gloss.inputs["Smooth"].default_value = 0.02
add = nt.nodes.new("ShaderNodeAddShader")
amb = nt.nodes.new("ShaderNodeEmission")
amb.inputs["Color"].default_value = (0.45, 0.2, 0.08, 1)
amb.inputs["Strength"].default_value = 0.6
add2 = nt.nodes.new("ShaderNodeAddShader")
outn = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(toon.outputs[0], add.inputs[0])
nt.links.new(gloss.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], add2.inputs[0])
nt.links.new(amb.outputs[0], add2.inputs[1])
nt.links.new(add2.outputs[0], outn.inputs[0])
for o in objs:
    o.data.materials.clear()
    o.data.materials.append(mat)

# Licht und Kamera
bpy.ops.object.light_add(type="SUN", location=(3, -3, 5))
bpy.context.object.data.energy = 2.5
bpy.context.object.rotation_euler = (0.8, 0.2, 0.6)
bpy.ops.object.camera_add(location=(0, -6, 1.2), rotation=(1.42, 0, 0))
scene.camera = bpy.context.object

world = bpy.data.worlds.new("Welt")
world.color = (0.03, 0.03, 0.03)  # kaum Umgebungslicht, damit Toon-Stufen sichtbar sind
scene.world = world

# Render: EEVEE braucht OpenGL, daher Cycles auf CPU + Freestyle-Linien
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16
scene.cycles.use_denoising = False
scene.render.resolution_x = scene.render.resolution_y = 768
scene.render.film_transparent = True  # freigestellt, Hintergrund frei waehlbar
scene.render.use_freestyle = True
scene.render.line_thickness = 2.2
vl = scene.view_layers[0]
vl.use_freestyle = True
tusche = bpy.data.linestyles.new("Tusche")
tusche.color = (0.08, 0.04, 0.02)
if not vl.freestyle_settings.linesets:
    vl.freestyle_settings.linesets.new("Konturen")
for ls in vl.freestyle_settings.linesets:
    ls.linestyle = tusche
    ls.select_by_visibility = True
    ls.select_silhouette = ls.select_border = ls.select_crease = True
scene.view_settings.view_transform = "Standard"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Fertig:", out)
