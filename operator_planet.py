import bpy
import bpy
import typing
from mathutils import *
import math
import bmesh


D = bpy.data
C = bpy.context






def createPlanet(context,input):
    nodeType = bpy.types.Node

    #create planet sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius =1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    ball = C.object

    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = input.levels
    bpy.context.object.modifiers["Subdivision"].render_levels = input.renderLevels
    
    return ball



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
    mat_planet.shadow_method = 'HASHED'

    #set Values in BSDF
    surfaceBSDF.inputs[15].default_value = 0.7 #transmission
    surfaceBSDF.inputs[7].default_value = 0.7 #roughness
    surfaceBSDF.inputs[5].default_value = 0.6 #specular
    
    if(forPlanet == True):
        surfacePattern(True,input.surfaceColorOne,input.surfaceColorTwo,input.surfaceScale,input.surfaceDetail, input.mappingX, input.mappingY, input.mappingZ, nodes, mat_planet, surfaceBSDF) 
        edgeTransparency(input.edgeTransparency, nodes, mat_planet, surfaceBSDF)
    else:
        mat_planet.blend_method = 'BLEND'
        surfacePattern(False, input.firstRingColor,input.secondRingColor,input.surfaceScaleRing, 4, 0, 1, 1, nodes, mat_planet, surfaceBSDF) 
    
    object.data.materials.append(mat_planet)

def surfacePattern(forPlanet, firstColor, secondColor, scale, detail, surfaceX, surfaceY, surfaceZ, nodes, mat_planet, surfaceBSDF):

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
    LowerSurfaceLimit = 0.4

    #set RGB for ColorRamp elements
    surfaceColorRamp.color_ramp.elements[0].color = firstColor
    surfaceColorRamp.color_ramp.elements[1].color = secondColor
    
    #link Nodes to BSDF
    if(forPlanet == True):
        mat_planet.node_tree.links.new(surfaceColorRamp.outputs[0],surfaceBSDF.inputs[0])
        mat_planet.node_tree.links.new(surfaceNoise.outputs[0],surfaceColorRamp.inputs[0])
        mat_planet.node_tree.links.new(surfaceMapping.outputs[0],surfaceNoise.inputs[0])
        mat_planet.node_tree.links.new(textureCoordinates.outputs[3],surfaceMapping.inputs[0])
    else:
        #create additional colorRamp for ring
        ringSurfaceColorRamp: nodeType = nodes.new("ShaderNodeValToRGB")
        
        ringSurfaceColorRamp.color_ramp.elements[0].color = firstColor
        ringSurfaceColorRamp.color_ramp.elements[1].color = secondColor
        
        ringSurfaceColorRamp.color_ramp.elements[0].position = 0.73
        ringSurfaceColorRamp.color_ramp.elements[1].position = 0.55
        #set Ring values
        
        #set values for Noise Texture for the Ring
        surfaceNoise.inputs[4].default_value = 0.2
        surfaceNoise.inputs[5].default_value = 0
        
        #set positions for ColorRamp elements for The Ring
        upperSurfaceLimit = 0.6
        LowerSurfaceLimit = 0.4
        
        #link Nodes to BSDF for Ring
        mat_planet.node_tree.links.new(textureCoordinates.outputs[2],surfaceMapping.inputs[0])
        mat_planet.node_tree.links.new(surfaceMapping.outputs[0],surfaceNoise.inputs[0])
        mat_planet.node_tree.links.new(surfaceNoise.outputs[0],surfaceColorRamp.inputs[0])
        mat_planet.node_tree.links.new(surfaceNoise.outputs[0],ringSurfaceColorRamp.inputs[0])
        mat_planet.node_tree.links.new(ringSurfaceColorRamp.outputs[0],surfaceBSDF.inputs[0])
        mat_planet.node_tree.links.new(surfaceColorRamp.outputs[0],surfaceBSDF.inputs[17])
        mat_planet.node_tree.links.new(surfaceColorRamp.outputs[0],surfaceBSDF.inputs[19])
        
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
    mat_planet.node_tree.links.new(edgeColorRamp.outputs[0],surfaceBSDF.inputs[19])
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






def createRingShape(innerRadius,outerRadius):


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

    for edge in bm.edges:
        if edge.is_boundary:
            # Calculate the average Z position of the edge vertices
            z_pos = (edge.verts[0].co.z + edge.verts[1].co.z) / 2
            if z_pos > 0:
                edge.select = True
                
    bpy.ops.transform.resize(value=(innerRadius, innerRadius, innerRadius))

    bpy.ops.mesh.select_all(action = 'DESELECT')
    lower_Edges= []
    for edge in bm.edges:
        if edge.is_boundary:
        
            z_pos = (edge.verts[0].co.z + edge.verts[1].co.z) / 2
            if z_pos <= 0:
                edge.select = True   
                lower_Edges.append(edge)  
    bpy.ops.transform.resize(value=(outerRadius, outerRadius, outerRadius))       

    for edge in lower_Edges:
        edge.verts[0].co.z = 0
        edge.verts[1].co.z = 0



    bmesh.update_edit_mesh(ringMesh)
    ringMesh.update()
    bpy.ops.object.editmode_toggle()



def main(context,input):
    planet = createPlanet(context,input)
    createPlanetMaterial(input,planet,True) 
    if input.hasRing:
        ring = createRing(context,input)
        createPlanetMaterial(input,ring,False)
        createRingShape(input.innerRadius, input.outerRadius)

class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"
    bl_options = {"REGISTER", "UNDO"}

  
   


    def execute(self, context):
        main(context,self)
        
        return {'FINISHED'}
    

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
    
    surfaceColorOne: bpy.props.FloatVectorProperty(
        name='surfaceColor 1',
        default=(1,0.35,0.1,1),
        min=0.0, max=1.0,
        subtype='COLOR',
        size=4,
        options={'SKIP_SAVE'}
    )
    
    surfaceColorTwo: bpy.props.FloatVectorProperty(
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
    
    
    
    innerRadius:bpy.props.FloatProperty(
        name='innerRadius',
        description='inner radius of the ring',
        default = (0.7),
        min= 0.01,
        max= 5,
        options={'SKIP_SAVE'})
        
    outerRadius:bpy.props.FloatProperty(
        name='outerRadius',
        description='outer radius of the ring',
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
        
    edgeTransparency:bpy.props.FloatProperty(
        name='edgeTransparency',
        description='edgeTransparency of the planet',
        default = (0.3),
        min= 0.1,
        max= 0.9,
        options={'SKIP_SAVE'})
    
    
    def draw(self, context):
        layout = self.layout
        layout.label(text='Subdivision Settings:')
        layout.prop(self, 'levels')
        layout.prop(self, 'renderLevels')
        layout.label(text='Surface Pattern:')
        layout.prop(self, 'mappingX')
        layout.prop(self, 'mappingY')
        layout.prop(self, 'mappingZ')
        layout.prop(self, 'surfaceDetail')
        layout.prop(self, 'surfaceScale')
        layout.prop(self, 'surfaceColorOne')
        layout.prop(self, 'surfaceColorTwo')
        layout.label(text='Ring Settings:')
        layout.prop(self, 'hasRing')
        if self.hasRing:
            layout.prop(self,'innerRadius')
            layout.prop(self,'outerRadius')
            layout.prop(self,'firstRingColor')
            layout.prop(self,'secondRingColor')
            layout.prop(self,'surfaceScaleRing')
        layout.label(text='Edge Settings:')
        layout.prop(self, 'edgeTransparency')
      
        
            

def menu_func(self, context):
    self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)




# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.types.VIEW3D_MT_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.types.VIEW3D_MT_add.remove(menu_func)


if __name__ == "__main__":
    register()
    
    
    
    

    
    
    
