# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####

import bpy

def bake_shadow(self, context):
    # This will create a negative shadow (Re-Volt requires a neg. texture)
    rd = context.scene.render
    rd.use_bake_to_vertex_color = False
    rd.use_textures = False

    shade_obj = context.object
    scene = bpy.context.scene

    resolution = shade_obj.revolt.shadow_resolution
    quality = shade_obj.revolt.shadow_quality
    method = shade_obj.revolt.shadow_method
    softness = shade_obj.revolt.shadow_softness

    # create hemi (positive)
    lamp_data_pos = bpy.data.lamps.new(name="ShadePositive", type="HEMI")
    lamp_positive = bpy.data.objects.new(name="ShadePositive", object_data=lamp_data_pos)

    lamp_data_neg = bpy.data.lamps.new(name="ShadeNegative", type="SUN")
    lamp_data_neg.use_negative = True
    lamp_data_neg.shadow_method = "RAY_SHADOW"
    lamp_data_neg.shadow_ray_samples = quality
    lamp_data_neg.shadow_ray_sample_method = method
    lamp_data_neg.shadow_soft_size = softness
    lamp_negative = bpy.data.objects.new(name="ShadeNegative", object_data=lamp_data_neg)

    scene.objects.link(lamp_positive)
    scene.objects.link(lamp_negative)

    # create a texture
    shadow_tex = bpy.data.images.new(name="Shadow", width=resolution, height=resolution)

    all_objs = [ob_child for ob_child in context.scene.objects if ob_child.parent == shade_obj] + [shade_obj]
    print([ob.matrix_local for ob in all_objs])

    # get the bounds taking in account all child objects (wheels, etc.)
    far_left = min([min([(ob.matrix_world[0][3] + ob.bound_box[i][0] * shade_obj.scale[0])  for i in range(0, 8)]) for ob in all_objs])
    far_right = max([max([(ob.matrix_world[0][3] + ob.bound_box[i][0] * shade_obj.scale[0])  for i in range(0, 8)]) for ob in all_objs])
    far_front = max([max([(ob.matrix_world[1][3] + ob.bound_box[i][1] * shade_obj.scale[1])  for i in range(0, 8)]) for ob in all_objs])
    far_back = min([min([(ob.matrix_world[1][3] + ob.bound_box[i][1] * shade_obj.scale[1])  for i in range(0, 8)]) for ob in all_objs])
    far_top = max([max([(ob.matrix_world[2][3] + ob.bound_box[i][2] * shade_obj.scale[2])  for i in range(0, 8)]) for ob in all_objs])
    far_bottom = min([min([(ob.matrix_world[2][3] + ob.bound_box[i][2] * shade_obj.scale[2])  for i in range(0, 8)]) for ob in all_objs])

    # get the dimensions to set the scale
    dim_x = abs(far_left - far_right)
    dim_y = abs(far_front - far_back)

    # location for the shadow plane
    loc = ((far_right + far_left)/2,
           (far_front + far_back)/2,
            far_bottom)

    # create the shadow plane and map it
    bpy.ops.mesh.primitive_plane_add(location=loc, enter_editmode=True)
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')
    shadow_plane = context.object

    # scale the shadow plane
    scale = max(dim_x, dim_y)
    shadow_plane.scale[0] = scale/1.5
    shadow_plane.scale[1] = scale/1.5
    print(shadow_plane.scale)

    for uv_face in context.object.data.uv_textures.active.data:
        uv_face.image = shadow_tex

    bpy.ops.object.bake_image()

    # And finally select it and delete it
    shade_obj.select = False
    shadow_plane.select = False
    lamp_positive.select = True
    lamp_negative.select = True
    bpy.ops.object.delete()

    # select the other object again
    shade_obj.select = True
    scene.objects.active = shade_obj

    # space between the car body center and the edge of the shadow plane
    sphor = (shadow_plane.location[0] - (shadow_plane.dimensions[0]/2))
    spver = ((shadow_plane.dimensions[1]/2) - shadow_plane.location[1])

    # generate shadowtable
    sleft = (sphor - shade_obj.location[0]) * 100
    sright = (shade_obj.location[0] - sphor) * 100
    sfront = (spver - shade_obj.location[1]) * 100
    sback = (shade_obj.location[1] - spver) * 100
    sheight = (far_bottom - shade_obj.location[2]) * 100
    shtable = ";)SHADOWTABLE {:4f} {:4f} {:4f} {:4f} {:4f}".format(sleft, sright, sfront, sback, sheight)
    shade_obj.revolt.shadow_table = shtable
