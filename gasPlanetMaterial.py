import bpy
import typing
from mathutils import *
D = bpy.data
C = bpy.context

#subdivison levels:
levels = 2
renderLevels = 2

#set surfacePattern
mappingX = 1
mappingY = 0.5
mappingZ = 0.2

surfaceDetail = 2.2

#surfacePattern colors

surfaceColorOne = (1,0.3,0.1,1)
surfaceColorTwo = (0.55,0.2,0.05,1)



#set transparency of edges (max 0.9)
transparency = 0.3

#BSDF values
transmission = 0.7



nodeType = bpy.types.Node;

#create sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius =1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
ball = C.object

bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision"].levels = levels
bpy.context.object.modifiers["Subdivision"].render_levels = renderLevels

def createMaterial(transmissionVal):
    #planet material generation
    mat_planet: bpy.types.Material = bpy.data.materials.new("Planet Material")
    mat_planet.use_nodes = True
    nodes: typing.List[bpy.types.Nodes] = mat_planet.node_tree.nodes
    surfaceBSDF: nodeType = nodes["Principled BSDF"]

    #set material Options to make planet look 'soft'
    mat_planet.use_screen_refraction = True
    mat_planet.blend_method = 'BLEND'
    mat_planet.show_transparent_back = False
    mat_planet.shadow_method = 'HASHED'

    #set Values in BSDF
    surfaceBSDF.inputs[15].default_value = transmissionVal
    surfaceBSDF.inputs[7].default_value = 0.7 #roughness
    surfaceBSDF.inputs[5].default_value = 0.6 #specular
    
    surfacePattern(surfaceColorOne, surfaceColorTwo, surfaceDetail, mappingX, mappingY, mappingZ, nodes, mat_planet, surfaceBSDF) 
    edgeTransparency(transparency, nodes, mat_planet, surfaceBSDF)
    
    ball.data.materials.append(mat_planet)

def surfacePattern(firstColor, secondColor, detail, surfaceX, surfaceY, surfaceZ, nodes, mat_planet, surfaceBSDF):

    #create Surface Pattern with Noise Texture and ColorRamp

    #create Noise Texture node
    surfaceNoise: nodeType = nodes.new("ShaderNodeTexNoise")

    #set values for Noise Texture
    surfaceNoise.inputs[2].default_value = 0.3
    surfaceNoise.inputs[3].default_value = detail
    surfaceNoise.inputs[4].default_value = 0.7
    surfaceNoise.inputs[5].default_value = 17

    #create ColorRamp node
    surfaceColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")

    #create Mapping node
    surfaceMapping: nodeType = nodes.new("ShaderNodeMapping");

    surfaceMapping.inputs[3].default_value[0] = surfaceX
    surfaceMapping.inputs[3].default_value[1] = surfaceY
    surfaceMapping.inputs[3].default_value[2] = surfaceZ

    #create coordinate Node
    textureCoordinates: nodeType = nodes.new("ShaderNodeTexCoord")

    #set positions for ColorRamp elements
    upperSurfaceLimit = 0.7
    LowerSurfaceLimit = 0.4
    surfaceColorRamp.color_ramp.elements[0].position = upperSurfaceLimit
    surfaceColorRamp.color_ramp.elements[1].position = LowerSurfaceLimit

    #set RGB for ColorRamp elements
    surfaceColorRamp.color_ramp.elements[0].color = firstColor
    surfaceColorRamp.color_ramp.elements[1].color = secondColor

    #link Nodes to BSDF
    mat_planet.node_tree.links.new(surfaceColorRamp.outputs[0],surfaceBSDF.inputs[0])
    mat_planet.node_tree.links.new(surfaceNoise.outputs[0],surfaceColorRamp.inputs[0])
    mat_planet.node_tree.links.new(surfaceMapping.outputs[0],surfaceNoise.inputs[0])
    mat_planet.node_tree.links.new(textureCoordinates.outputs[3],surfaceMapping.inputs[0])


#make edges transparent - Gas planet
def edgeTransparency(diff, nodes, mat_planet, surfaceBSDF):

    #create Layer Weight Node
    layerWeight: nodeType = nodes.new("ShaderNodeLayerWeight")

    #create ColorRamp node
    edgeColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")

    #set positions for ColorRamp elements
    upperLimit = 0.95
    lowerLimit = upperLimit - diff 
    edgeColorRamp.color_ramp.elements[0].position = upperLimit
    edgeColorRamp.color_ramp.elements[1].position = lowerLimit

    #link Nodes to BSDF
    mat_planet.node_tree.links.new(edgeColorRamp.outputs[0],surfaceBSDF.inputs[19])
    mat_planet.node_tree.links.new(layerWeight.outputs[1],edgeColorRamp.inputs[0])

    #set ColorRamp to Ease
    edgeColorRamp.color_ramp.interpolation = 'EASE'
    
createMaterial(transmission)
