import bpy
import typing
from mathutils import *
D = bpy.data
C = bpy.context

nodeType = bpy.types.Node;

#create sphere
icosphere =    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=6, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

ball = C.object

#planet material generation
mat_planet: bpy.types.Material = bpy.data.materials.new("Planet Material")
mat_planet.use_nodes = True
nodes: typing.List[bpy.types.Nodes] = mat_planet.node_tree.nodes
continentBSDF: nodeType = nodes["Principled BSDF"]

textureCoordinates: nodeType = nodes.new("ShaderNodeTexCoord")
earthNoise:nodeType = nodes.new("ShaderNodeTexNoise")

earthNoise.inputs[2].default_value= 2.6
earthNoise.inputs[3].default_value= 16.0
earthNoise.inputs[4].default_value= 5.7

earthyColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")

earthyColorRamp.color_ramp.elements[0].position = 0.4
earthyColorRamp.color_ramp.elements[1].position = 0.7


mat_planet.node_tree.links.new(textureCoordinates.outputs[3],earthNoise.inputs[0])


mat_planet.node_tree.links.new(earthNoise.outputs[0],earthyColorRamp.inputs[0])

mat_planet.node_tree.links.new(earthyColorRamp.outputs[0],continentBSDF.inputs[0])

ball.data.materials.append(mat_planet)