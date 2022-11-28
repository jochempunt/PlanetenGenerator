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

#testnode: bpy.types.ColorRamp.elements.new()

earthyColorRamp.color_ramp.elements[0].position = 0.433
earthyColorRamp.color_ramp.elements[1].position = 0.7
earthyColorRamp.color_ramp.elements.new(0.6)
#die position des elements ist die wie weit es links ist 

earthyColorRamp.color_ramp.elements[0].color = (0.017,0.1,0.026,1)
earthyColorRamp.color_ramp.elements[1].color = (0.4,0.129,0.056,1)
earthyColorRamp.color_ramp.elements[2].color = (0.23,0.060,0.016,1)
# colors in RGBA format



#continent/earth color
mat_planet.node_tree.links.new(textureCoordinates.outputs[3],earthNoise.inputs[0])
mat_planet.node_tree.links.new(earthNoise.outputs[0],earthyColorRamp.inputs[0])
mat_planet.node_tree.links.new(earthyColorRamp.outputs[0],continentBSDF.inputs[0])

#continent Bumps
continentBumpNoise:nodeType = nodes.new("ShaderNodeTexNoise")
mat_planet.node_tree.links.new(textureCoordinates.outputs[3],continentBumpNoise.inputs[0])

continentBumpNoise.inputs[2].default_value= 50.0
continentBumpNoise.inputs[3].default_value= 16.0
continentBumpNoise.inputs[4].default_value= 5.7




bumpNode: nodeType = nodes.new("ShaderNodeBump")
bumpNode.inputs[0].default_value = 0.095

mat_planet.node_tree.links.new(continentBumpNoise.outputs[0], bumpNode.inputs[2])
mat_planet.node_tree.links.new(bumpNode.outputs[0], continentBSDF.inputs[22])

#Todo Ozeane Wolken & Atmosphäre
# Einstellbare Parameter / UI
#Gasplanet & Ringe
#Mond
#Sterne?
#Laufzeit??

ball.data.materials.append(mat_planet)