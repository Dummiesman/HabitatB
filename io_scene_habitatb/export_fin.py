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

    # write the number of instances
    file.write(struct.pack("<L", len(instances)))
    print("Exporting", len(instances), "instances.")

    for instance in instances:

        # prepare the name. only the first 9 letters are stored in upper case
        name = path.splitext(instance.data.name)[0][:9 - 1].upper()

        # get the rotation matrix
        rot_matrix = instance.matrix_world
        rot_matrix = helpers.get_rot_matrix(rot_matrix)

        # get the position from the world matrix (takes child transl. into account)
        pos = Vector(helpers.get_pos_from_matrix(instance.matrix_world)) * matrix
        flag = 0
        col_red = int(instance.revolt.fin_col[0] * 255)
        col_green = int(instance.revolt.fin_col[1] * 255)
        col_blue = int(instance.revolt.fin_col[2] * 255)

        env_red = int(instance.revolt.fin_envcol[0] * 255)
        env_green = int(instance.revolt.fin_envcol[1] * 255)
        env_blue = int(instance.revolt.fin_envcol[2] * 255)
        env_alpha = int((1-instance.revolt.fin_envcol[3]) * 255)

        priority = instance.revolt.fin_priority

        # apply the flags
        if instance.revolt.fin_flag_env:
            flag |= const.FIN_ENV
        if instance.revolt.fin_flag_hide:
            flag |= const.FIN_HIDE
        if instance.revolt.fin_flag_no_mirror:
            flag |= const.FIN_NO_MIRROR
        if instance.revolt.fin_flag_no_lights:
            flag |= const.FIN_NO_LIGHTS
        if instance.revolt.fin_flag_no_object_coll:
            flag |= const.FIN_NO_OBJECT_COLLISION
        if instance.revolt.fin_flag_no_camera_coll:
            flag |= const.FIN_NO_CAMERA_COLLISION
        if instance.revolt.fin_flag_model_rgb:
            flag |= const.FIN_SET_MODEL_RGB
        lod_bias = instance.revolt.fin_lod_bias

        # write the file
        name = str.encode(name)
        file.write(struct.pack("<9s", name))
        file.write(struct.pack("<3B", col_red, col_green, col_blue))
        file.write(struct.pack("<4B", env_red, env_green, env_blue, env_alpha))

        # writ the priority and the flag with padding
        file.write(struct.pack("<BBxx", priority, flag))
        file.write(struct.pack("<f", lod_bias))
        file.write(struct.pack("<3f", *pos))
        file.write(struct.pack("<9f", *rot_matrix))



######################################################
# EXPORT
######################################################
def save_fin(filepath, context, matrix):

    time1 = time.clock()

    ob = bpy.context.active_object
    print("exporting FIN: {}...".format(filepath))

    # write the actual data
    file = open(filepath, "wb")
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


    return {"FINISHED"}
