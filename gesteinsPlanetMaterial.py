import bpy
import typing
from mathutils import *

D = bpy.data
C = bpy.context

nodeType = bpy.types.Node;

#create sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius =1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

planet = C.object

bpy.ops.mesh.primitive_uv_sphere_add(radius =1.02, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

atmos = C.object

earthNoiseScale = 2.6
earthNoiseDetail = 16.0
earthNoiseRoughness = 5.7
earthColor1 = (0.017,0.1,0.026,1)
earthColor2 =  (0.4,0.129,0.056,1)
earthColor3 = (0.23,0.060,0.016,1)

continentBumpyness = 0.2
continentsScaleX = 0.6
continentsScaleY = 1.0
continentsScaleZ = 1.0
amountOfContinents = 0.5
continentDivision = 0.57
continentHeight = 0.35


oceanColor1 = (0.009,0.019,0.122,1)
oceanColor2 = (0.047,0.136,0.384,1)
shoreSize = 0.06 #0.0 biggest
wavyness = 0.03

cloudDivision = 3.5
cloudsize = 0.12
cloudColor = (0.8,0.8,0.8,0.8)

atmosphereAlpha = 0.3
atmoshereSize = 0.050
atmosphereColor =(0.050,0.279,1.0,1)

bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision"].levels = 3



#planet material generation

def createGesteinsPlanet(_planet):
    mat_planet: bpy.types.Material = bpy.data.materials.new("Planet Material")
    mat_planet.use_nodes = True
    nodes: typing.List[bpy.types.Nodes] = mat_planet.node_tree.nodes
    continentBSDF: nodeType = nodes["Principled BSDF"]
    textureCoordinates: nodeType = nodes.new("ShaderNodeTexCoord")
    earthNoise:nodeType = nodes.new("ShaderNodeTexNoise")
    earthNoise.inputs[2].default_value= earthNoiseScale
    earthNoise.inputs[3].default_value= earthNoiseDetail
    earthNoise.inputs[4].default_value= earthNoiseRoughness
    earthyColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")
    earthyColorRamp.color_ramp.elements[0].position = 0.433
    earthyColorRamp.color_ramp.elements[1].position = 0.7
    earthyColorRamp.color_ramp.elements.new(0.6)
    #die position des elements ist die wie weit es links ist 

    earthyColorRamp.color_ramp.elements[0].color = earthColor1
    earthyColorRamp.color_ramp.elements[1].color = earthColor2
    earthyColorRamp.color_ramp.elements[2].color = earthColor3
    # colors in RGBA format

    #continent/earth color
    mat_planet.node_tree.links.new(textureCoordinates.outputs[3],earthNoise.inputs[0])
    mat_planet.node_tree.links.new(earthNoise.outputs[0],earthyColorRamp.inputs[0])
    mat_planet.node_tree.links.new(earthyColorRamp.outputs[0],continentBSDF.inputs[0])

    #continent Bumps
    planetBumpNoise:nodeType = nodes.new("ShaderNodeTexNoise")

    planetBumpNoise.inputs[2].default_value= 50.0
    planetBumpNoise.inputs[3].default_value= 16.0
    planetBumpNoise.inputs[4].default_value= 0.572
    planetBumpNoise.inputs[5].default_value= 0

    mat_planet.node_tree.links.new(textureCoordinates.outputs[3],planetBumpNoise.inputs[0])


    bumpNode: nodeType = nodes.new("ShaderNodeBump")
    bumpNode.inputs[0].default_value = continentBumpyness
    mat_planet.node_tree.links.new(planetBumpNoise.outputs[0], bumpNode.inputs[2])


    #Continents
    continentMapping: nodeType = nodes.new("ShaderNodeMapping");
    mat_planet.node_tree.links.new(textureCoordinates.outputs[3],continentMapping.inputs[0])



    continentMapping.inputs[3].default_value[0] = continentsScaleX
    continentMapping.inputs[3].default_value[1] = continentsScaleY
    continentMapping.inputs[3].default_value[2] = continentsScaleZ

    continentNoise: nodeType = nodes.new("ShaderNodeTexNoise");
    mat_planet.node_tree.links.new(continentMapping.outputs[0],continentNoise.inputs[0])

    continentNoise.inputs[2].default_value= amountOfContinents
    continentNoise.inputs[3].default_value= 15.6
    continentNoise.inputs[4].default_value= continentDivision
    continentNoise.inputs[5].default_value= 0.2

    continentMaskColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")

    mat_planet.node_tree.links.new(continentNoise.outputs[0],continentMaskColorRamp.inputs[0])

    continentMaskColorRamp.color_ramp.elements[0].position = 0.545
    continentMaskColorRamp.color_ramp.elements[1].position = 0.561

    continentBumpNode:nodeType = nodes.new("ShaderNodeBump")

    continentBumpNode.inputs[0].default_value = continentHeight
    mat_planet.node_tree.links.new(continentMaskColorRamp.outputs[0], continentBumpNode.inputs[2])
    mat_planet.node_tree.links.new(bumpNode.outputs[0], continentBumpNode.inputs[3])


    mat_planet.node_tree.links.new(earthyColorRamp.outputs[0],continentBSDF.inputs[0])

    mountainBumpNode:nodeType = nodes.new("ShaderNodeBump")

    mat_planet.node_tree.links.new(continentBumpNode.outputs[0], continentBSDF.inputs[20])

    #Ozean
    oceanColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")
    mat_planet.node_tree.links.new(continentNoise.outputs[0],oceanColorRamp.inputs[0])

    oceanColorRamp.color_ramp.elements[0].position = 0.525
    # distance beteweem these elements is the size of the "shore/beaches"
    oceanColorRamp.color_ramp.elements[1].position = oceanColorRamp.color_ramp.elements[0].position + shoreSize

    oceanColorRamp.color_ramp.elements[0].color = oceanColor1
    oceanColorRamp.color_ramp.elements[1].color = oceanColor2

    oceanBSDF: nodeType = nodes.new("ShaderNodeBsdfPrincipled")
    mat_planet.node_tree.links.new(oceanColorRamp.outputs[0],oceanBSDF.inputs[0])
    ##metalic
    oceanBSDF.inputs[4].default_value = 0.355
    ##roughness
    oceanBSDF.inputs[7].default_value = 0.595


    #Waves for the ocean
    wavesNoise: nodeType = nodes.new("ShaderNodeTexNoise")
    wavesNoise.inputs[2].default_value= 70.0
    wavesNoise.inputs[3].default_value= 15.0
    wavesNoise.inputs[4].default_value= 0.40
    wavesNoise.inputs[5].default_value= 0.0
    mat_planet.node_tree.links.new(textureCoordinates.outputs[3],wavesNoise.inputs[0])

    wavesBumps: nodeType  = nodes.new("ShaderNodeBump")

    wavesBumps.inputs[0].default_value = wavyness
    mat_planet.node_tree.links.new(wavesNoise.outputs[0],wavesBumps.inputs[2])
    mat_planet.node_tree.links.new(wavesBumps.outputs[0],oceanBSDF.inputs[20])

    earthOceanMixShader: nodeType = nodes.new("ShaderNodeMixShader")
    mat_planet.node_tree.links.new(continentMaskColorRamp.outputs[0],earthOceanMixShader.inputs[0])
    mat_planet.node_tree.links.new(oceanBSDF.outputs[0],earthOceanMixShader.inputs[1])
    mat_planet.node_tree.links.new(continentBSDF.outputs[0],earthOceanMixShader.inputs[2])

    materialOutput: nodeType = nodes["Material Output"]
    mat_planet.node_tree.links.new(earthOceanMixShader.outputs[0],materialOutput.inputs[0])
    _planet.data.materials.append(mat_planet)




def createAtmosphere(_atmosphere,_clouds):
   
    
    
    mat_Cloud: bpy.types.Material = bpy.data.materials.new("Cloud Material")
    mat_Cloud.use_nodes = True
    nodesC: typing.List[bpy.types.Nodes] = mat_Cloud.node_tree.nodes
    
    
    atmoMask: nodeType = nodesC.new("ShaderNodeValToRGB")
    
    #Atmosphere
    atmoLayerWeight: nodeType = nodesC.new("ShaderNodeLayerWeight")

    atmoLayerWeight.inputs[0].default_value = atmosphereAlpha

  
    
    mat_Cloud.node_tree.links.new(atmoLayerWeight.outputs[0],atmoMask.inputs[0])

    atmoMask.color_ramp.elements[0].position = atmoshereSize
    atmoMask.color_ramp.elements[1].position = 0.808

    atmoBSDF: nodeType = nodesC.new("ShaderNodeBsdfPrincipled")
    #mat_Cloud.node_tree.links.new(oceanColorRamp.outputs[0],oceanBSDF.inputs[0])

    atmoBSDF.inputs[0].default_value = atmosphereColor # atmosphere color
   
    if _clouds == True:
        #Clouds
       

        textureCoordinatesC: nodeType = nodesC.new("ShaderNodeTexCoord")
        #PuffyClouds
        cloudShapeNoise: nodeType = nodesC.new("ShaderNodeTexNoise")
        mat_Cloud.node_tree.links.new(textureCoordinatesC.outputs[3],cloudShapeNoise.inputs[0])

        cloudShapeNoise.inputs[2].default_value = cloudDivision
        cloudShapeNoise.inputs[3].default_value = 16.0
        cloudShapeNoise.inputs[4].default_value = 0.65
        cloudShapeMaskRamp: nodeType = nodesC.new("ShaderNodeValToRGB")
        mat_Cloud.node_tree.links.new(cloudShapeNoise.outputs[0],cloudShapeMaskRamp.inputs[0])
        cloudShapeMaskRamp.color_ramp.elements[0].position = 0.36

        cloudShapeMaskRamp.color_ramp.elements[1].position = cloudShapeMaskRamp.color_ramp.elements[0].position + cloudsize

        cloudPatternNoise:nodeType = nodesC.new("ShaderNodeTexNoise")
        cloudPatternNoise.inputs[2].default_value = 5.0
        cloudPatternNoise.inputs[3].default_value = 16.0
        cloudPatternNoise.inputs[4].default_value = 0.720
        cloudPatternNoise.inputs[5].default_value = 0.1
        mat_Cloud.node_tree.links.new(textureCoordinatesC.outputs[3],cloudPatternNoise.inputs[0])

        cloudPatternVoronoi: nodeType = nodesC.new("ShaderNodeTexVoronoi")
        cloudPatternVoronoi.inputs[2].default_value = 1.9
        mat_Cloud.node_tree.links.new(cloudPatternNoise.outputs[0],cloudPatternVoronoi.inputs[0])

        cloudMixColor: nodeType = nodesC.new("ShaderNodeMixRGB")
        cloudMixColor.inputs[2].default_value = (0,0,0,1)
        mat_Cloud.node_tree.links.new(cloudPatternVoronoi.outputs[0],cloudMixColor.inputs[1])
        mat_Cloud.node_tree.links.new(cloudShapeMaskRamp.outputs[0],cloudMixColor.inputs[0])

        ##Cloud Material

        mat_Cloud.use_screen_refraction = True
        mat_Cloud.blend_method = 'BLEND'
        mat_Cloud.show_transparent_back = False
        mat_Cloud.shadow_method = 'HASHED'

        cloudBSDF: nodeType = nodesC["Principled BSDF"]
        cloudBSDF.inputs[0].default_value = cloudColor
        cloudBSDF.inputs[7].default_value = 0.65

        cloudBumpNoise: nodeType = nodesC.new("ShaderNodeTexNoise")
        cloudBumpNoise.inputs[2].default_value = 45.0
        cloudBumpNoise.inputs[3].default_value = 16.0
        cloudBumpNoise.inputs[4].default_value = 0.397
        mat_Cloud.node_tree.links.new(textureCoordinatesC.outputs[3],cloudBumpNoise.inputs[0])

        cloudBumps: nodeType  = nodesC.new("ShaderNodeBump")
        cloudBumps.inputs[0].default_value = 0.002 #bumpyness of clouds
        mat_Cloud.node_tree.links.new(cloudBumpNoise.outputs[0],cloudBumps.inputs[2])
        mat_Cloud.node_tree.links.new(cloudBumps.outputs[0],cloudBSDF.inputs[20])

        transparentDSDF: nodeType = nodesC.new("ShaderNodeBsdfTransparent")

        cloudMixShader: nodeType = nodesC.new("ShaderNodeMixShader")

        mat_Cloud.node_tree.links.new(cloudMixColor.outputs[0],cloudMixShader.inputs[0])

        mat_Cloud.node_tree.links.new(transparentDSDF.outputs[0],cloudMixShader.inputs[1])
        mat_Cloud.node_tree.links.new(cloudBSDF.outputs[0],cloudMixShader.inputs[2])

        materialOutputC: nodeType = nodesC["Material Output"]
        # mat_Cloud.node_tree.links.new(cloudMixShader.outputs[0],materialOutputC.inputs[0])



        planetAtmoMixShader: nodeType = nodesC.new("ShaderNodeMixShader")
        mat_Cloud.node_tree.links.new(atmoMask.outputs[0],planetAtmoMixShader.inputs[0])
        mat_Cloud.node_tree.links.new(cloudMixShader.outputs[0],planetAtmoMixShader.inputs[1])
        mat_Cloud.node_tree.links.new(atmoBSDF.outputs[0],planetAtmoMixShader.inputs[2])



        mat_Cloud.node_tree.links.new(planetAtmoMixShader.outputs[0],materialOutputC.inputs[0])

    else:
        materialOutputC: nodeType = nodesC["Material Output"]
        planetAtmoMixShader: nodeType = nodesC.new("ShaderNodeMixShader")
        mat_Cloud.node_tree.links.new(atmoMask.outputs[0],planetAtmoMixShader.inputs[0])
        transparentDSDF: nodeType = nodesC.new("ShaderNodeBsdfTransparent")
        mat_Cloud.node_tree.links.new(transparentDSDF.outputs[0],planetAtmoMixShader.inputs[1])
        mat_Cloud.node_tree.links.new(atmoBSDF.outputs[0],planetAtmoMixShader.inputs[2])
        mat_Cloud.node_tree.links.new(atmoBSDF.outputs[0],materialOutputC.inputs[0])



  
  

    _atmosphere.data.materials.append(mat_Cloud)





createGesteinsPlanet(planet)
createAtmosphere(atmos,True)