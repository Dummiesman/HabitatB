
# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import bpy, struct, bmesh, re, os, glob
import time, struct
from mathutils import Vector, Matrix, Color

from . import const, parameters, import_prm, helpers

export_filename = None

######################################################
# IMPORT MAIN FILES
######################################################
def load_fin_file(filepath, context, matrix):
    fails = [] # failed import names
    file = open(filepath, 'rb')
    scn = bpy.context.scene
    context = bpy.context
    folder = os.sep.join(filepath.split(os.sep)[:-1])

    # check for reversed folder
    if folder.split(os.sep)[-1] == "reversed":
        print("Reversed folder detected.")
        folder = os.sep.join(filepath.split(os.sep)[:-2])

    # hide the relationship lines because they're not easy on the eyes
    # this doesn't work with the context of the file menu, obviously
    # I think it's better to add it as an option in the side panel.
    # context.space_data.show_relationship_lines = False


    # read amount of instances
    instance_count = struct.unpack('<L', file.read(4))[0]

    if instance_count == 0:
        helpers.msg_box(const.STR_EMPTY_FIN)
        return 0

    # Create an empty object and parent all instance objects to it.
    # This is done to prevent clutter in the object outliner.
    fin_parent = bpy.data.objects.new(name=filepath.split(os.sep)[-1], object_data=None)
    bpy.context.scene.objects.link(fin_parent)

    for instance in range(instance_count):
        # get the file name of the instance
        prm_name = struct.unpack('<9s', file.read(9))[0]
        prm_name = str(prm_name, encoding='ascii').split('\x00', 1)[0]
        print("Importing instance {} of {}: {}".format(instance+1, instance_count, prm_name))

        # get the model color
        red_col, green_col, blue_col = struct.unpack('<3B', file.read(3))
        # get the env color of the instance, includes alpha
        blue_env, green_env, red_env, alpha_env = struct.unpack('<4B', file.read(4))

        # other props
        priority, flag = struct.unpack('<BBxx', file.read(4)) # two bytes with padding
        lod_bias = struct.unpack('<f', file.read(4))[0]
        pos = Vector(struct.unpack("<3f", file.read(12)))
        rot_matrix = Matrix((struct.unpack('<3f', file.read(12)),
                             struct.unpack('<3f', file.read(12)),
                             struct.unpack('<3f', file.read(12))))

        # find correct file if prm name is too long
        prm_fname = None
        for fl in os.listdir(folder):
            if prm_name.lower() == fl.split(".")[0][:8].lower() and ".prm" in fl:
                prm_fname = fl
                break

        imported_obj = None
        if prm_fname in [ob.name for ob in context.scene.objects]:
            # if the PRM has been imported already, use the object data of the existing object instead
            ob_data = context.scene.objects[prm_fname].data
            imported_obj = bpy.data.objects.new(name=prm_fname, object_data=ob_data)
            imported_obj.revolt.rv_type = "INSTANCE"
            bpy.context.scene.objects.link(imported_obj)
        elif prm_fname in os.listdir(folder):
            try:
                instance_path = os.sep.join([folder, prm_fname])
                import_prm.load_prm(instance_path, context, matrix, rvtype="INSTANCE")
                imported_obj = context.object
            except:
                # something went wrong while importing
                print("Import of {} failed.".format(prm_fname))
                fails.append(prm_name)
        else:
            # the file could not be found
            print("Import of {} failed because it was not found.".format(prm_fname))
            fails.append(prm_name)

        if imported_obj:
            # set all properties and flags
            imported_obj.matrix_world = helpers.to_trans_matrix(rot_matrix)
            imported_obj.location = pos*matrix
            imported_obj.revolt.fin_priority = priority
            imported_obj.revolt.fin_lod_bias = lod_bias
            imported_obj.revolt.fin_col = (red_col / 255, green_col / 255, blue_col / 255)
            imported_obj.revolt.fin_envcol = (red_env / 255, green_env / 255, blue_env / 255, 1-alpha_env / 255)

            imported_obj.revolt.fin_flag_env = bool(flag & const.FIN_ENV)
            imported_obj.revolt.fin_flag_hide = bool(flag & const.FIN_HIDE)
            imported_obj.revolt.fin_flag_no_mirror = bool(flag & const.FIN_NO_MIRROR)
            imported_obj.revolt.fin_flag_no_lights = bool(flag & const.FIN_NO_LIGHTS)
            imported_obj.revolt.fin_flag_no_camera_coll = bool(flag & const.FIN_NO_OBJECT_COLLISION)
            imported_obj.revolt.fin_flag_no_object_coll = bool(flag & const.FIN_NO_CAMERA_COLLISION)

            # set the object's parent to the empty fin object
            imported_obj.parent = fin_parent

    if fails:
        helpers.msg_box("The following instances could not be imported:{}".format(
                        *["\n"+fail for fail in fails]))


######################################################
# IMPORT
######################################################
def load_fin(filepath, context, matrix):

    print("importing fin: %r..." % (filepath))

    time1 = time.clock()

    # start reading the fin file
    load_fin_file(filepath, context, matrix)

    print(" done in %.4f sec." % (time.clock() - time1))

def load(operator, filepath, context, matrix):

    global export_filename
    export_filename = filepath

    load_fin(filepath, context, matrix)

    helpers.enable_texture_mode()

    return {'FINISHED'}
