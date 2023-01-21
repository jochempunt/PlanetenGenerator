import bpy
import typing
from mathutils import *
import math
import bmesh


D = bpy.data
C = bpy.context

nodeType = bpy.types.Node;




def createPlanet(context,input):
    nodeType = bpy.types.Node

    #create planet sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius =1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    ball = C.object

    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = input.levels
    bpy.context.object.modifiers["Subdivision"].render_levels = input.renderLevels
    
    return ball

def createAtmosphere(context,input):
    bpy.ops.mesh.primitive_uv_sphere_add(radius =1.02, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    atmos = C.object
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = input.levels
    bpy.context.object.modifiers["Subdivision"].render_levels = input.renderLevels

    return atmos

def createRing(context,input):
    C.object.select_set(False)
    #create ring
    bpy.ops.mesh.primitive_uv_sphere_add(radius =2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    ring = C.object


    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = input.levels
    bpy.context.object.modifiers["Subdivision"].render_levels = input.renderLevels
    
    
    return ring


def createPlanetMaterial(input,object, forPlanet):
    #planet material generation
    mat_planet: bpy.types.Material = bpy.data.materials.new("Planet Material")
    mat_planet.use_nodes = True
    nodes: typing.List[bpy.types.Nodes] = mat_planet.node_tree.nodes
    surfaceBSDF: nodeType = nodes["Principled BSDF"]

    #set material Options to make planet look 'soft'
    mat_planet.use_screen_refraction = True
    mat_planet.blend_method = 'BLEND'
    
        
    mat_planet.show_transparent_back = False
    mat_planet.shadow_method = 'NONE'

    #set Values in BSDF
    surfaceBSDF.inputs[15].default_value = 0.7 #transmission
    surfaceBSDF.inputs[7].default_value = 0.7 #roughness
    surfaceBSDF.inputs[5].default_value = 0.6 #specular
    
    if(forPlanet == True):
        surfacePattern(input,True,input.surfaceColor1,input.surfaceColor2,input.surfaceScale,input.surfaceDetail, input.mappingX, input.mappingY, input.mappingZ, nodes, mat_planet, surfaceBSDF) 
        edgeTransparency(input.edgeTransparency, nodes, mat_planet, surfaceBSDF)
    else:
        mat_planet.blend_method = 'HASHED'
        if input.isHashed == False:
            mat_planet.blend_method = 'BLEND'
        surfacePattern(input,False, input.firstRingColor,input.secondRingColor,input.surfaceScaleRing, 4, 0, 1, 1, nodes, mat_planet, surfaceBSDF) 
        
    object.data.materials.append(mat_planet)

def surfacePattern(input,forPlanet, firstColor, secondColor, scale, detail, surfaceX, surfaceY, surfaceZ, nodes, mat_planet, surfaceBSDF):

    #create Surface Pattern with Noise Texture and ColorRamp

    #create Noise Texture node
    surfaceNoise: nodeType = nodes.new("ShaderNodeTexNoise")

    #set values for Noise Texture
    surfaceNoise.inputs[2].default_value = scale
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

    LowerSurfaceLimit = 0.2
  
    #set RGB for ColorRamp elements
    surfaceColorRamp.color_ramp.elements[0].color = firstColor
    surfaceColorRamp.color_ramp.elements[1].color = secondColor

   
    

    
    #link Nodes to BSDF
    if(forPlanet == True):
        if input.numberOfColors == 1:
            surfaceColorRamp.color_ramp.elements.remove(surfaceColorRamp.color_ramp.elements[1])
      
            

          
        mat_planet.node_tree.links.new(surfaceColorRamp.outputs[0],surfaceBSDF.inputs[0])
        mat_planet.node_tree.links.new(surfaceNoise.outputs[0],surfaceColorRamp.inputs[0])
        mat_planet.node_tree.links.new(surfaceMapping.outputs[0],surfaceNoise.inputs[0])
        mat_planet.node_tree.links.new(textureCoordinates.outputs[3],surfaceMapping.inputs[0])
        surfaceColorRamp.color_ramp.elements[0].position = upperSurfaceLimit
        if input.numberOfColors > 1:
            surfaceColorRamp.color_ramp.elements[1].position = LowerSurfaceLimit
       
    else:
        #create additional colorRamp for ring
        
        ringSurfaceColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")
        
        surfaceColorRamp.color_ramp.elements[0].color = (1, 1, 1, 1)
        surfaceColorRamp.color_ramp.elements[1].color = (0, 0, 0, 1)
        
        
        ringSurfaceColorRamp.color_ramp.elements[0].color = firstColor
        ringSurfaceColorRamp.color_ramp.elements[1].color = secondColor
        
        ringSurfaceColorRamp.color_ramp.elements[0].position = 0.73
        ringSurfaceColorRamp.color_ramp.elements[1].position = 0.55
        #set Ring values
        
        #set values for Noise Texture for the Ring
        surfaceNoise.inputs[4].default_value = 0.2
        surfaceNoise.inputs[5].default_value = 0
        
        #set positions for ColorRamp elements for The Ring
        upperSurfaceLimit = 0.8
        LowerSurfaceLimit = 0.4
        
        #link Nodes to BSDF for Ring
        mat_planet.node_tree.links.new(textureCoordinates.outputs[2],surfaceMapping.inputs[0])
        mat_planet.node_tree.links.new(surfaceMapping.outputs[0],surfaceNoise.inputs[0])
        mat_planet.node_tree.links.new(surfaceNoise.outputs[0],surfaceColorRamp.inputs[0])
        mat_planet.node_tree.links.new(surfaceNoise.outputs[0],ringSurfaceColorRamp.inputs[0])
        mat_planet.node_tree.links.new(ringSurfaceColorRamp.outputs[0],surfaceBSDF.inputs[0])
        mat_planet.node_tree.links.new(surfaceColorRamp.outputs[0],surfaceBSDF.inputs[21])
        surfaceColorRamp.color_ramp.elements[0].position = upperSurfaceLimit
        surfaceColorRamp.color_ramp.elements[1].position = LowerSurfaceLimit
   

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
    mat_planet.node_tree.links.new(edgeColorRamp.outputs[0],surfaceBSDF.inputs[21])
    mat_planet.node_tree.links.new(layerWeight.outputs[1],edgeColorRamp.inputs[0])

    #set ColorRamp to Ease
    edgeColorRamp.color_ramp.interpolation = 'EASE'






def angle_between_vector_and_ground_plane(vector):
    # Calculate the angle between the vector and the ground plane (the xy-plane)
    
    dot_product = vector[0]*0 + vector[1]*0 + vector[2]*1
    vector_length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    cos_angle = dot_product / vector_length
    angle = math.acos(cos_angle)
    
    # Convert the angle to degrees
    angle_degrees = angle * 180 / math.pi
    
    return angle_degrees





def createRingShape(thickness,size):

    bpy.ops.object.editmode_toggle() 
    ring = bpy.context.edit_object
    ringMesh = ring.data
    bm = bmesh.from_edit_mesh(ringMesh)
    bpy.ops.mesh.select_all(action = 'DESELECT')

    for face in bm.faces:
        angle = angle_between_vector_and_ground_plane(face.normal)
        if angle  >90 and angle <100:
            face.select = False
        else:
            face.select = True
    faces_select = [f for f in bm.faces if f.select] 
    bmesh.ops.delete(bm, geom=faces_select, context="FACES") 
    bpy.ops.mesh.select_all(action = 'DESELECT')
    
    for upper_edge in bm.edges:
        if upper_edge.is_boundary:
            # Calculate the average Z position of the edge vertices
            z_pos = (upper_edge.verts[0].co.z + upper_edge.verts[1].co.z) / 2
            if z_pos == 0:
                upper_edge.select = True             
    bpy.ops.transform.resize(value=(thickness, thickness, 0))

    for edge in bm.edges:
        if edge.is_boundary:
            z_pos = (edge.verts[0].co.z + edge.verts[1].co.z) / 2
            if z_pos <= 0:
                edge.select = True
                edge.verts[0].co.z = 0
                edge.verts[1].co.z = 0   
                
    bpy.ops.transform.resize(value=(size, size, 0))       
    bmesh.update_edit_mesh(ringMesh)
    ringMesh.update()
    bpy.ops.object.editmode_toggle() 


#gesteinsplanet


def createGesteinsPlanet(_planet,input):
    mat_planet: bpy.types.Material = bpy.data.materials.new("Planet Material")
    mat_planet.use_nodes = True
    nodes: typing.List[bpy.types.Nodes] = mat_planet.node_tree.nodes
    continentBSDF: nodeType = nodes["Principled BSDF"]
    textureCoordinates: nodeType = nodes.new("ShaderNodeTexCoord")
    earthNoise:nodeType = nodes.new("ShaderNodeTexNoise")
    earthNoise.inputs[2].default_value= input.earthNoiseScale
    earthNoise.inputs[3].default_value= input.earthNoiseDetail
    earthNoise.inputs[4].default_value= input.earthNoiseRoughness
    earthyColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")
    earthyColorRamp.color_ramp.elements[0].position = 0.433
    earthyColorRamp.color_ramp.elements[1].position = 0.7
    earthyColorRamp.color_ramp.elements.new(0.6)
    #die position des elements ist die wie weit es links ist 

    earthyColorRamp.color_ramp.elements[0].color = input.earthColor1
    earthyColorRamp.color_ramp.elements[1].color = input.earthColor2
    earthyColorRamp.color_ramp.elements[2].color = input.earthColor3
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
    bumpNode.inputs[0].default_value = input.continentBumpyness
    mat_planet.node_tree.links.new(planetBumpNoise.outputs[0], bumpNode.inputs[2])


    #Continents
    continentMapping: nodeType = nodes.new("ShaderNodeMapping");
    mat_planet.node_tree.links.new(textureCoordinates.outputs[3],continentMapping.inputs[0])



    continentMapping.inputs[3].default_value[0] = input.continentsScaleX
    continentMapping.inputs[3].default_value[1] = input.continentsScaleY
    continentMapping.inputs[3].default_value[2] = input.continentsScaleZ

    continentNoise: nodeType = nodes.new("ShaderNodeTexNoise");
    mat_planet.node_tree.links.new(continentMapping.outputs[0],continentNoise.inputs[0])

    continentNoise.inputs[2].default_value= input.amountOfContinents
    continentNoise.inputs[3].default_value= 15.6
    continentNoise.inputs[4].default_value= input.continentDivision
    continentNoise.inputs[5].default_value= 0.2

    continentMaskColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")

    mat_planet.node_tree.links.new(continentNoise.outputs[0],continentMaskColorRamp.inputs[0])


    oceanAmount = input.oceanAmount *  0.555;
    continentMaskColorRamp.color_ramp.elements[0].position = oceanAmount
    continentMaskColorRamp.color_ramp.elements[1].position = 0.561

    continentBumpNode:nodeType = nodes.new("ShaderNodeBump")

    continentBumpNode.inputs[0].default_value = input.continentHeight
    mat_planet.node_tree.links.new(continentMaskColorRamp.outputs[0], continentBumpNode.inputs[2])
    mat_planet.node_tree.links.new(bumpNode.outputs[0], continentBumpNode.inputs[3])


    mat_planet.node_tree.links.new(earthyColorRamp.outputs[0],continentBSDF.inputs[0])

 

    mat_planet.node_tree.links.new(continentBumpNode.outputs[0], continentBSDF.inputs[22])

    #Ozean
    oceanColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")
    mat_planet.node_tree.links.new(continentNoise.outputs[0],oceanColorRamp.inputs[0])

    oceanColorRamp.color_ramp.elements[0].position = 0.525
    # distance beteweem these elements is the size of the "shore/beaches"
    oceanColorRamp.color_ramp.elements[1].position = oceanColorRamp.color_ramp.elements[0].position + input.shoreSize

    oceanColorRamp.color_ramp.elements[0].color = input.oceanColor1
    oceanColorRamp.color_ramp.elements[1].color = input.oceanColor2

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

    wavesBumps.inputs[0].default_value = input.wavyness
    mat_planet.node_tree.links.new(wavesNoise.outputs[0],wavesBumps.inputs[2])
    mat_planet.node_tree.links.new(wavesBumps.outputs[0],oceanBSDF.inputs[22])

    earthOceanMixShader: nodeType = nodes.new("ShaderNodeMixShader")
    mat_planet.node_tree.links.new(continentMaskColorRamp.outputs[0],earthOceanMixShader.inputs[0])
    mat_planet.node_tree.links.new(oceanBSDF.outputs[0],earthOceanMixShader.inputs[1])
    mat_planet.node_tree.links.new(continentBSDF.outputs[0],earthOceanMixShader.inputs[2])

    materialOutput: nodeType = nodes["Material Output"]
    mat_planet.node_tree.links.new(earthOceanMixShader.outputs[0],materialOutput.inputs[0])
    _planet.data.materials.append(mat_planet)

def atmospherePattern(_atmosphere,_clouds,input):
   
    
    
    mat_Cloud: bpy.types.Material = bpy.data.materials.new("Cloud Material")
    mat_Cloud.use_nodes = True
    nodesC: typing.List[bpy.types.Nodes] = mat_Cloud.node_tree.nodes
    
    
    atmoMask: nodeType = nodesC.new("ShaderNodeValToRGB")
    
    #Atmosphere
    atmoLayerWeight: nodeType = nodesC.new("ShaderNodeLayerWeight")

    atmoLayerWeight.inputs[0].default_value = input.atmosphereAlpha

  
    
    mat_Cloud.node_tree.links.new(atmoLayerWeight.outputs[0],atmoMask.inputs[0])

    atmoMask.color_ramp.elements[0].position = input.atmoshereSize
    atmoMask.color_ramp.elements[1].position = 0.808

    atmoBSDF: nodeType = nodesC.new("ShaderNodeBsdfPrincipled")
    #mat_Cloud.node_tree.links.new(oceanColorRamp.outputs[0],oceanBSDF.inputs[0])

    atmoBSDF.inputs[0].default_value =input.atmosphereColor # atmosphere color
   
    if _clouds == True:
        #Clouds
       

        textureCoordinatesC: nodeType = nodesC.new("ShaderNodeTexCoord")
        #PuffyClouds
        cloudShapeNoise: nodeType = nodesC.new("ShaderNodeTexNoise")
        mat_Cloud.node_tree.links.new(textureCoordinatesC.outputs[3],cloudShapeNoise.inputs[0])

        cloudShapeNoise.inputs[2].default_value = input.cloudDivision
        cloudShapeNoise.inputs[3].default_value = 16.0
        cloudShapeNoise.inputs[4].default_value = 0.65
        cloudShapeMaskRamp: nodeType = nodesC.new("ShaderNodeValToRGB")
        mat_Cloud.node_tree.links.new(cloudShapeNoise.outputs[0],cloudShapeMaskRamp.inputs[0])
        cloudShapeMaskRamp.color_ramp.elements[0].position = 0.36

        cloudShapeMaskRamp.color_ramp.elements[1].position = cloudShapeMaskRamp.color_ramp.elements[0].position + input.cloudsize

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
        cloudBSDF.inputs[0].default_value = input.cloudColor
        cloudBSDF.inputs[7].default_value = 0.65

        cloudBumpNoise: nodeType = nodesC.new("ShaderNodeTexNoise")
        cloudBumpNoise.inputs[2].default_value = 45.0
        cloudBumpNoise.inputs[3].default_value = 16.0
        cloudBumpNoise.inputs[4].default_value = 0.397
        mat_Cloud.node_tree.links.new(textureCoordinatesC.outputs[3],cloudBumpNoise.inputs[0])

        cloudBumps: nodeType  = nodesC.new("ShaderNodeBump")
        cloudBumps.inputs[0].default_value = 0.002 #bumpyness of clouds
        mat_Cloud.node_tree.links.new(cloudBumpNoise.outputs[0],cloudBumps.inputs[2])
        mat_Cloud.node_tree.links.new(cloudBumps.outputs[0],cloudBSDF.inputs[22])

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

def main(context,input):
    planet = createPlanet(context,input)
    if input.planeten_art == "GASPLANET": 
        createPlanetMaterial(input,planet,True) 
        if input.hasRing:
            ring = createRing(context,input)
            createPlanetMaterial(input,ring,False)
            createRingShape(input.thickness, input.ringSize)
    elif input.planeten_art == "GESTEINSPLANET":
        createGesteinsPlanet(planet,input)
        amtosphere = createAtmosphere(context,input)
        atmospherePattern(amtosphere,True,input)

class PlanetenGenerator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.planeten_generator"
    bl_label = "Planeten-Generator"
    bl_options = {"REGISTER", "UNDO"}

  
   


    def execute(self, context):
        main(context,self)
        
        return {'FINISHED'}
    

    planeten_art: bpy.props.EnumProperty(
        name="Art",
        description="Choose one of the options",
        items=[("GASPLANET", "Gasplanet ", ""),
               ("GESTEINSPLANET", "Gesteinsplanet", "")
               ],
        default="GASPLANET"
    )




    #Subdivision Settings    
    levels: bpy.props.IntProperty(
        name='levels',
        description='amount of subdivision',
        default = (2),
        min= 1,
        max= 10) 
        
    renderLevels:bpy.props.IntProperty(
        name='render levels',
        description='amount of subdivision in render view',
        default = (2),
        min= 1,
        max= 10)
    #set surfacePattern
    
    
    mappingX:bpy.props.FloatProperty(
        name='mappingX',
        description='mappingX of the pattern',
        default = (1),
        min= 0,
        max= 10,
        options={'SKIP_SAVE'})
      
    mappingY:bpy.props.FloatProperty(
        name='mappingY',
        description='mappingY of the pattern',
        default = (0.5),
        min= 0,
        max= 10,
        options={'SKIP_SAVE'})
    
    mappingZ:bpy.props.FloatProperty(
        name='mappingZ',
        description='mappingZ of the pattern',
        default = (0.5),
        min= 0,
        max= 10,
        options={'SKIP_SAVE'})
    
    surfaceDetail:bpy.props.FloatProperty(
        name='surface Detail',
        description='how detailed the pattern will be',
        default = (2.2),
        min= 0.01,
        max= 5,
        options={'SKIP_SAVE'})
    
    surfaceScale:bpy.props.FloatProperty(
        name='surface Scale',
        description='scale of the pattern',
        default = (0.3),
        min= 0.01,
        max= 5,
        options={'SKIP_SAVE'})
    
    surfaceColor1: bpy.props.FloatVectorProperty(
        name='surfaceColor 1',
        default=(1,0.35,0.1,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )
    
    surfaceColor2: bpy.props.FloatVectorProperty(
        name='surfaceColor 2',
        default=(0.4, 0.3, 0.07,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )
    
   
    
    #ring variables
    hasRing: bpy.props.BoolProperty(
        name='has_Ring',     
        default=True,
        options={'SKIP_SAVE'})
    
    
    
    thickness:bpy.props.FloatProperty(
        name='thickness',
        description='how thick the width of the ring is',
        default = (0.7),
        min= 0.01,
        max= 5,
        options={'SKIP_SAVE'})
        
    ringSize:bpy.props.FloatProperty(
        name='ringSize',
        description='impacts the total size of the ring',
        default = (1.2),
        min= 0.01,
        max= 5,
        options={'SKIP_SAVE'})
        
        
    firstRingColor: bpy.props.FloatVectorProperty(
        name='firstRingColor',
        default=(1,0.35,0.1,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )
    
    
    
    
    secondRingColor:bpy.props.FloatVectorProperty(
        name='secondRingColor',
        default=(0.4, 0.3, 0.07,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )
    
    
    surfaceScaleRing:bpy.props.FloatProperty(
        name='surfaceScaleRing',
        description='surface Scale of the Ring',
        default = (105),
        min= 1,
        max= 300,
        options={'SKIP_SAVE'})
        
        
        
    isHashed: bpy.props.BoolProperty(
        name='isHashed',     
        default=True,
        options={'SKIP_SAVE'})
        
    edgeTransparency:bpy.props.FloatProperty(
        name='edgeTransparency',
        description='edgeTransparency of the planet',
        default = (0.3),
        min= 0.1,
        max= 0.9,
        options={'SKIP_SAVE'})
    
    
    #Gesteinsplanet
    
    
    earthNoiseScale:bpy.props.FloatProperty(
        name='earthNoiseScale',
        description='inner radius of the ring',
        default = (2.6),
        min= 0.01,
        max= 5,
        options={'SKIP_SAVE'})
    
    earthNoiseDetail:bpy.props.FloatProperty(
        name='earthNoiseDetail',
        description='inner radius of the ring',
        default = (16.0),
        min= 1,
        max= 40,
        options={'SKIP_SAVE'}) 
    
 
    earthNoiseRoughness:bpy.props.FloatProperty(
        name='earthNoiseRoughness',
        description='inner radius of the ring',
        default = (5.7),
        min= 1,
        max= 20,
        options={'SKIP_SAVE'}) 
        
    numberOfColors:bpy.props.IntProperty(
        name='numberOfColors',
        description='amount of colors used',
        default = (2),
        min= 1,
        max= 2,
        options={'SKIP_SAVE'}) 
    
 
    
    earthColor1:bpy.props.FloatVectorProperty(
        name='earthColor1',
        default=(0.017,0.1,0.026,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    ) 
    
    earthColor2:bpy.props.FloatVectorProperty(
        name='earthColor2',
        default=(0.4,0.129,0.056,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    ) 
          
    earthColor3:bpy.props.FloatVectorProperty(
        name='earthColor3',
        default=(0.23,0.060,0.016,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    ) 
           
    #continents
    
    continentBumpyness:bpy.props.FloatProperty(
        name='continentBumpyness',
        description='how bumpy the continents are',
        default = (0.06),
        min= 0,
        max= 0.2,
        options={'SKIP_SAVE'}) 
    
    
     
   
    continentsScaleX:bpy.props.FloatProperty(
        name='continentsScaleX',
        description='continentsScaleX',
        default = (0.6),
        min= -1,
        max= 4,
        options={'SKIP_SAVE'}) 
    
    continentsScaleY:bpy.props.FloatProperty(
        name='continentsScaleY',
        description='continentsScaleY',
        default = (1),
        min= -1,
        max= 4,
        options={'SKIP_SAVE'}) 
    
    continentsScaleZ:bpy.props.FloatProperty(
        name='continentsScaleZ',
        description='continentsScaleZ',
        default = (1),
        min= -1.00,
        max= 4,
        options={'SKIP_SAVE'}) 
       
    amountOfContinents:bpy.props.FloatProperty(
        name='amountOfContinents',
        description='amount of continents',
        default = (0.5),
        min= 0.01,
        max= 10,
        options={'SKIP_SAVE'}) 
    
    

    continentDivision:bpy.props.FloatProperty(
        name='continent detail',
        description='how much detail the continent shapes have',
        default = (0.57),
        min= 0.01,
        max= 1,
        options={'SKIP_SAVE'}) 
    
 
    continentHeight:bpy.props.FloatProperty(
        name='continentHeight',
        description='continentHeight',
        default = (0.35 ),
        min= 0.01,
        max= 1,
        options={'SKIP_SAVE'}) 
  #ozeane


    oceanAmount:bpy.props.FloatProperty(
        name='oceanAmount',
        description='how much water is on the planet, 0 is a dried out planet',
        default = (0.85),
        min= 0.0,
        max= 1.0,
        options={'SKIP_SAVE'}) 


    oceanColor1:bpy.props.FloatVectorProperty(
        name='oceanColor1',
        default=(0.009,0.019,0.122,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )   
  
    oceanColor2:bpy.props.FloatVectorProperty(
        name='oceanColor2',
        default=(0.047,0.136,0.384,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )   
    
    shoreSize:bpy.props.FloatProperty(
        name='shoreSize',
        description='shoreSize - 0.0 is biggest',
        default = (0.06),
        min= 0.0,
        max= 0.1,
        options={'SKIP_SAVE'})     
        
    wavyness:bpy.props.FloatProperty(
        name='wavyness',
        description='shoreSize - 0.0 is biggest',
        default = (0.02),
        min= 0.0,
        max= 0.1,
        options={'SKIP_SAVE'})   

    cloudDivision:bpy.props.FloatProperty(
        name='cloudDivision',
        description='cloudDivision',
        default = (3.5),
        min= 0.1,
        max= 10,
        options={'SKIP_SAVE'})   
    
    cloudsize:bpy.props.FloatProperty(
        name='cloudsize',
        description='cloudsize, 0 is no clouds at all',
        default = (0.12),
        min= 0.,
        max= 1,
        options={'SKIP_SAVE'})  

    cloudColor:bpy.props.FloatVectorProperty(
        name='cloudColor',
        default=(0.8,0.8,0.8,0.8),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )   

    atmosphereAlpha:bpy.props.FloatProperty(
        name='atmosphereAlpha',
        description='how transparent the atmosphere is',
        default = (0.3),
        min= 0.0,
        max= 0.9,
        options={'SKIP_SAVE'})   
    
    atmoshereSize:bpy.props.FloatProperty(
        name='atmoshereSize',
        description='how big the border of the actual atmosphere shows',
        default = (0.05),
        min= 0.0,
        max= 0.2,
        options={'SKIP_SAVE'})   

    atmosphereColor:bpy.props.FloatVectorProperty(
        name='atmosphereColor',
        default=(0.050,0.279,1.0,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'})  


  
           
    
    
    
    def draw(self, context):
        layout = self.layout
        layout.label(text='Subdivision Settings:')
        layout.prop(self, 'levels')
        layout.prop(self, 'renderLevels')
        layout.prop(self, "planeten_art", expand=False)
        if self.planeten_art == "GASPLANET":
            layout.label(text='Surface Pattern:')
            layout.prop(self, 'mappingX')
            layout.prop(self, 'mappingY')
            layout.prop(self, 'mappingZ')
            layout.prop(self, 'surfaceDetail')
            layout.prop(self, 'surfaceScale')
            layout.prop(self, 'numberOfColors')
            for i  in range (self.numberOfColors):
                  layout.prop(self, 'surfaceColor'+ str(i+1))
            layout.label(text='Ring Settings:')
            layout.prop(self, 'hasRing')
            if self.hasRing:
                layout.prop(self,'thickness')
                layout.prop(self,'ringSize')
                layout.prop(self,'firstRingColor')
                layout.prop(self,'secondRingColor')
                layout.prop(self,'surfaceScaleRing')
                layout.prop(self,'isHashed')
                
            layout.label(text='Edge Settings:')
            layout.prop(self, 'edgeTransparency')
        elif self.planeten_art == "GESTEINSPLANET":
            layout.label(text='Ground Pattern:')
            layout.prop(self, 'earthNoiseScale')
            layout.prop(self, 'earthNoiseDetail')
            layout.prop(self, 'earthNoiseRoughness')
            layout.prop(self, 'earthColor1')
            layout.prop(self, 'earthColor2')
            layout.prop(self, 'earthColor3')
            layout.label(text='Continents:')
            layout.prop(self, 'continentBumpyness')
            layout.prop(self, 'continentsScaleX')
            layout.prop(self, 'continentsScaleY')
            layout.prop(self, 'continentsScaleZ')
            layout.prop(self, 'amountOfContinents')
            layout.prop(self, 'continentDivision')
            layout.prop(self, 'continentHeight')
            layout.label(text='Oceans:')
            layout.prop(self, 'oceanAmount')
            layout.prop(self, 'oceanColor1')
            layout.prop(self, 'oceanColor2')
            layout.prop(self, 'shoreSize')
            layout.prop(self, 'wavyness')
            layout.label(text='Clouds:')
            layout.prop(self, 'cloudDivision')
            layout.prop(self, 'cloudsize')
            layout.prop(self, 'cloudColor')
            layout.label(text='Atmosphere:')
            layout.prop(self, 'atmosphereAlpha')
            layout.prop(self, 'atmoshereSize')
            layout.prop(self, 'atmosphereColor')
        




            

def menu_func(self, context):
    self.layout.operator(PlanetenGenerator.bl_idname, text=PlanetenGenerator.bl_label)




# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(PlanetenGenerator)
    bpy.types.VIEW3D_MT_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(PlanetenGenerator)
    bpy.types.VIEW3D_MT_add.remove(menu_func)


if __name__ == "__main__":
    register()
    
    
    
    

    
    
    
