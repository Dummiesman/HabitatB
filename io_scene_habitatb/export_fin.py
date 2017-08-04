# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import time, struct, math
import os.path as path

import bpy, bmesh
from mathutils import Color, Vector, Matrix
from . import helpers, const

######################################################
# EXPORT MAIN FILES
######################################################

def save_fin_file(file, context, matrix):

    scn = bpy.context.scene
    instances = [] # list of objects to export_objs

    # add all instances to the list
    for obj in context.scene.objects:
        if obj.revolt.rv_type == "INSTANCE":
            instances.append(obj)

    file.write(struct.pack(len(instances), "<L"))

    for instance in instances:
        name = os.path.splitext(ob.data.name)[0][:9 - 1].upper()
        matrix = ob.matrix_world * matrix
        pos = ob.location * matrix # get from matrix_w
        flag = 0
        col_red, col_green, col_blue = ob.revolt.fin_col
        env_red, env_green, env_blue, env_alpha = ob.revolt.fin_envcol
        priority = ob.revolt.fin_priority
        if ob.revolt.fin_flag_env:
            flag |= INSTANCE_ENV
        if ob.revolt.fin_flag_hide:
            flag |= INSTANCE_HIDE
        if ob.revolt.fin_flag_no_mirror:
            flag |= INSTANCE_NO_MIRROR
        if ob.revolt.fin_flag_no_lights:
            flag |= INSTANCE_NO_LIGHTS
        if ob.revolt.fin_flag_no_object_coll:
            flag |= INSTANCE_NO_OBJECT_COLLISION
        if ob.revolt.fin_flag_no_camera_coll:
            flag |= INSTANCE_NO_CAMERA_COLLISION
        if ob.revolt.fin_flag_model_rgb:
            flag |= INSTANCE_SET_MODEL_RGB
        lod_bias = ob.revolt.fin_lod_bias

        name = str.encode(name)
        file.write(struct.pack('<9s', name))
        file.write(struct.pack('<3B', red, green, blue))
        env_rgb.write_data(file)
        file.write(struct.pack('<BBxx', priority, flag))
        file.write(struct.pack('<f', lod_bias))
        file.write(struct.pack('<fff', pos[0]))
        matrix.write_data(file)

    print("Exporting", len(instances), "instances.")


######################################################
# EXPORT
######################################################
def save_fin(filepath, context, matrix):

    time1 = time.clock()

    ob = bpy.context.active_object
    print("exporting FIN: {}...".format(filepath))

    # write the actual data
    file = open(filepath, 'wb')
    save_fin_file(file, context, matrix)
    file.close()

    # fin export complete
    print(" done in %.4f sec." % (time.clock() - time1))


def save(operator, filepath, context, matrix):

    # save FIN file

    if "INSTANCE" in helpers.get_object_types(context):
        save_fin(filepath, context, matrix)
    else:
        helpers.msg_box(const.STR_NO_FIN)


    return {'FINISHED'}
