import bpy
import bmesh
import math



def angle_between_vector_and_ground_plane(vector):
    # Calculate the angle between the vector and the ground plane (i.e., the xy-plane)
    # The angle is calculated using the dot product between the vector and the normal vector of the ground plane (i.e., (0, 0, 1))
    dot_product = vector[0]*0 + vector[1]*0 + vector[2]*1
    vector_length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    cos_angle = dot_product / vector_length
    angle = math.acos(cos_angle)
    
    # Convert the angle to degrees
    angle_degrees = angle * 180 / math.pi
    
    return angle_degrees

bpy.ops.mesh.primitive_uv_sphere_add(radius =2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

bpy.ops.object.editmode_toggle()    
obj = bpy.context.edit_object
mesh = obj.data
bm = bmesh.from_edit_mesh(mesh)


bpy.ops.mesh.select_all(action = 'DESELECT')


for face in bm.faces:
    angle = angle_between_vector_and_ground_plane(face.normal)
    if angle  >90 and angle <100:
        face.select = False
    else:
        face.select = True
faces_select = [f for f in bm.faces if f.select] 
bmesh.ops.delete(bm, geom=faces_select, context="FACES")  

bmesh.update_edit_mesh(mesh)
mesh.update()
bpy.ops.object.editmode_toggle()