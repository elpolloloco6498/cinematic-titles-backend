# Test Automation Blender

import bpy
import os
import sys

# LAUNCH
# blender --background --python exportSceneGltf.py "TEXT"

# CONFIGURATION
TEXT = sys.argv[1:][3]
EXTRUDE = 0.15
BEVEL = 0.005
REMESH_RES = 0.008

COLOR = "C:/Users/seeds/PycharmProjects/blenderAutomationTest/textures/metal_plates/color.jpg"
METALNESS = "C:/Users/seeds/PycharmProjects/blenderAutomationTest/textures/metal_plates/metalness.jpg"
ROUGHNESS = "C:/Users/seeds/PycharmProjects/blenderAutomationTest/textures/metal_plates/roughness.jpg"
DISPLACEMENT = "C:/Users/seeds/PycharmProjects/blenderAutomationTest/textures/metal_plates/displacement.jpg"
HDRI = "C:/Users/seeds/PycharmProjects/blenderAutomationTest/hdri/pizzo_pernice_4k.exr"

SNAPSHOT_FILE = "test.png"
RENDER_PATH = f"C:/Users/seeds/PycharmProjects/blenderAutomationTest/{SNAPSHOT_FILE}"
EXPORT_SCENE_PATH = f"C:/Users/seeds/PycharmProjects/blenderAutomationTest/scene.gltf"

# delete default cube in scene
bpy.ops.object.delete(use_global=False)

# CREATE TEXT OBJECT
bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
text = bpy.context.scene.objects['Text']
text.rotation_euler[0] = 1.5708
text.data.align_x = 'CENTER'
# rename text
text.data.body = TEXT
# change font

# extrude text
text.data.extrude = EXTRUDE
# bevel text
text.data.bevel_resolution = 8
text.data.bevel_depth = BEVEL

# CONVERT TO MESH
bpy.ops.object.convert(target='MESH')

# TODO amélioration : séparer chaque lettre, pour chaque lettre faire les UV et appliquer le même matériau
# REMESH TOPOLOGY
bpy.ops.object.modifier_add(type='REMESH')
bpy.context.object.modifiers["Remesh"].voxel_size = REMESH_RES
bpy.ops.object.modifier_apply(modifier="Remesh")

# UV MAPPING
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.cube_project(cube_size=0.475158)

# MATERIAL
mat = bpy.data.materials.new(name='Gold')
mat.use_nodes = True
# material assignment
text.active_material = mat

bsdf = mat.node_tree.nodes.get("Principled BSDF")
# pbr material : (Base Color, Metalness, Roughness, Displacement)
baseColor = mat.node_tree.nodes.new("ShaderNodeTexImage")
baseColor.image = bpy.data.images.load(COLOR)
mat.node_tree.links.new(bsdf.inputs['Base Color'], baseColor.outputs['Color'])

metalness = mat.node_tree.nodes.new("ShaderNodeTexImage")
metalness.image = bpy.data.images.load(METALNESS)
mat.node_tree.links.new(bsdf.inputs['Metallic'], metalness.outputs['Color'])

roughness = mat.node_tree.nodes.new("ShaderNodeTexImage")
roughness.image = bpy.data.images.load(ROUGHNESS)
mat.node_tree.links.new(bsdf.inputs['Roughness'], roughness.outputs['Color'])

displacement = mat.node_tree.nodes.new("ShaderNodeTexImage")
displacement.image = bpy.data.images.load(DISPLACEMENT)
# create displacement node
displacementNode = mat.node_tree.nodes.new("ShaderNodeDisplacement")
# get material output
materialOutput = mat.node_tree.nodes.get("Material Output")
# link
mat.node_tree.links.new(displacementNode.inputs['Height'], displacement.outputs['Color'])
mat.node_tree.links.new(materialOutput.inputs['Displacement'], displacementNode.outputs['Displacement'])
displacementNode.inputs[2].default_value = 0.015
# set size texture
texCoord = mat.node_tree.nodes.new("ShaderNodeTexCoord")
texMapping = mat.node_tree.nodes.new("ShaderNodeMapping")
mat.node_tree.links.new(texMapping.inputs['Vector'], texCoord.outputs['UV'])
mat.node_tree.links.new(baseColor.inputs['Vector'], texMapping.outputs['Vector'])
mat.node_tree.links.new(metalness.inputs['Vector'], texMapping.outputs['Vector'])
mat.node_tree.links.new(roughness.inputs['Vector'], texMapping.outputs['Vector'])
mat.node_tree.links.new(displacement.inputs['Vector'], texMapping.outputs['Vector'])
texMapping.inputs[3].default_value = (0.1, 0.1, 0.1)

# LIGHTING
# point light
light = bpy.context.scene.objects['Light']
light.location = (0.32, 4, 0.27)
light.data.color = (1, 0.158868, 0.076779) # red light

# environment lighting HDRI
world = bpy.data.worlds['World']
envTexture = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
envTexture.image = bpy.data.images.load(HDRI)
background = world.node_tree.nodes["Background"]
worldOutput = world.node_tree.nodes["World Output"]
world.node_tree.links.new(background.inputs['Color'], envTexture.outputs['Color'])
world.node_tree.links.new(worldOutput.inputs['Surface'], background.outputs['Background'])

# use scene lights and env
for s in bpy.data.screens:
    for a in s.areas:
        if a.type=='VIEW_3D':
            a.spaces[0].shading.use_scene_lights_render = True
            a.spaces[0].shading.use_scene_world_render = True

# CAMERA
# camera orientation
cam = bpy.context.scene.camera
cam.rotation_euler = (1.5708, 0, 0)

# camera position
cam.location = (0, -8, 0)

# RENDER
# render configuration
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.film_transparent = True

# render snapshot

#print("RENDERING IMAGE...")
"""
scene = bpy.context.scene
scene.render.image_settings.file_format="PNG"
scene.render.filepath = RENDER_PATH
bpy.ops.render.render(write_still=1)
"""
print(RENDER_PATH)

#export scene gltf
bpy.ops.export_scene.gltf(filepath=os.path.join(os.getcwd(), "scene.gltf"), export_format="GLTF_EMBEDDED")


