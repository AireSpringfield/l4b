import bpy
from mathutils import *
from transform import *
import math



root_obj = None
turtle_mat = Matrix.Identity(4)


def matrixof(transform: Transform):
    if type(transform) == RotateX:
        return Matrix.Rotation(math.radians(transform.angle), 4, 'X')
    elif type(transform) == RotateY:
        return Matrix.Rotation(math.radians(transform.angle), 4, 'Y')
    elif type(transform) == RotateZ:
        return Matrix.Rotation(math.radians(transform.angle), 4, 'Z')
    elif type(transform) == Forward:
        return Matrix.Translation(Vector((0.0, 0.0, transform.length, 1.0)))


def interpret(lstring, objname=''):
    empty_mesh = bpy.data.meshes.new(objname)
    global root_obj
    mat_stack = []

    root_obj = bpy.data.objects.new(objname, empty_mesh)
    scene = bpy.context.scene
    scene.collection.objects.link(root_obj)

    def _interpret(nested_list: list):
        global turtle_mat
        for item in nested_list:
            #print(item)
            #print(turtle_mat)
            if isinstance(item, list):
                mat_stack.append(Matrix(turtle_mat))  # Push
                _interpret(item)
                turtle_mat = mat_stack.pop()  # Pop
            elif isinstance(item, Transform):
                if isinstance(item, Lookat):
                    turtle_pos = turtle_mat[3].xyz
                    turtle_to_target = (item.target - turtle_pos).normalized()
                    turtle_mat_new = Matrix()
                    turtle_mat_new.col[3] = turtle_mat.col[3]
                    turtle_mat_new.col[2] = turtle_to_target.resized(4)
                    old_y = turtle_mat.col[1].xyz.normalized()
                    new_x = Vector.cross(old_y, turtle_to_target)
                    new_y = Vector.cross(turtle_to_target, new_x)
                    turtle_mat_new.col[1] = new_y.resized(4)
                    turtle_mat_new.col[0] = new_x.resized(4)
                    turtle_mat = turtle_mat_new
                else:
                # Note the order: Transforms are "local" - last appear, first apply
                    turtle_mat @= matrixof(item)
            else:
                item.draw()

    _interpret(lstring)


def draw_object(meshobj, scale=1):
    if meshobj not in bpy.data.objects.keys():
        raise KeyError('No object named {}.'.format(meshobj))

    mesh = bpy.data.objects[meshobj]
    mesh_mat = mesh.matrix_world
    scene = bpy.context.scene
    new_obj = bpy.data.objects.new('', mesh.data)
    new_obj.matrix_world = mesh_mat
    scene.collection.objects.link(new_obj)

    # TODO: shader
    new_obj.matrix_world = turtle_mat @ new_obj.matrix_world
    new_obj.scale *= scale

    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    new_obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj
    bpy.ops.object.join()

def draw_internode_straight(length, radius=0.3):
    global turtle_mat

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length)
    cyl = bpy.context.object
    # position origin at base
    #bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    cyl.select_set(True)
    bpy.ops.transform.translate(value=(0, 0, length/2))
    #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    cyl.matrix_world = turtle_mat @ cyl.matrix_world

    turtle_mat @= matrixof(Forward(length))

    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    cyl.select_set(True)
    bpy.context.view_layer.objects.active = root_obj
    bpy.ops.object.join()


def draw_curve(end_point, end_tangent, radius=0.1):  # in world space
    global turtle_mat

    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
    curve = bpy.context.object
    curve.matrix_world = turtle_mat @ curve.matrix_world

    spline = curve.data.splines[0]

    # beg_point: (0, 0, 0)
    # beg_tangent: (0, 0, 1)

    point0 = spline.bezier_points[0]
    point0.co = Vector((0,0,0))
    point0.handle_left_type = 'FREE'
    point0.handle_right_type = 'FREE'
    point0.handle_left = Vector((0,0,-0.5))
    point0.handle_right = Vector((0, 0, 0.5))



    mat_world2local = curve.matrix_world.inverted()
    point1 = spline.bezier_points[1]
    point1.co = (mat_world2local @ end_point).xyz
    point1.handle_left_type = 'FREE'
    point1.handle_right_type = 'FREE'
    tangent = (mat_world2local @ end_tangent).xyz.normalized()
    point1.handle_left = point1.co - 0.5*tangent
    point1.handle_right = point1.co + 0.5*tangent

    curve.data.bevel_depth = radius



    bpy.ops.object.convert(target='MESH')

    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    curve.select_set(True)
    bpy.context.view_layer.objects.active = root_obj
    bpy.ops.object.join()
    # Modify turtle, origin at end_point, z pointing end_tangent
    # Do it when interpreting curved internode, in module-defined functions
