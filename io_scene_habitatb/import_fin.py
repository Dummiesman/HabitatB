
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
def load_fin_file(filepath, matrix):
    file = open(filepath, 'rb')
    scn = bpy.context.scene
    context = bpy.context
    folder = os.sep.join(filepath.split(os.sep)[:-1])

    # read header
    instance_count = struct.unpack('<L', file.read(4))[0]

    for instance in range(instance_count):
        # get the file name of the instance
        prm_name = struct.unpack('<9s', file.read(9))[0]
        prm_name = str(prm_name, encoding='ascii').split('\x00', 1)[0]

        # get the model color
        red, green, blue = struct.unpack('<3B', file.read(3))
        # get the env color of the instance
        blue, green, red, alpha = struct.unpack('<BBBB', file.read(4))

        # other props
        priority, flag = struct.unpack('<BBxx', file.read(4))
        lod_bias = struct.unpack('<f', file.read(4))[0]
        pos = Vector(struct.unpack("<3f", file.read(12)))
        rot_matrix = Matrix((struct.unpack('<3f', file.read(12)),
                             struct.unpack('<3f', file.read(12)),
                             struct.unpack('<3f', file.read(12))))

        # find correct file if prm name is too long
        prm_fname = None
        for fl in os.listdir(folder):
            if prm_name.lower() in fl[:9].lower() and ".prm" in fl:
                prm_fname = fl
                break

        # check if it actually es
        if prm_fname in os.listdir(folder):
            infstance_path = os.sep.join([folder, prm_fname])
            import_prm.load_prm(infstance_path, context, matrix, rvtype="INSTANCE")

            context.object.matrix_world = helpers.to_trans_matrix(rot_matrix)
            context.object.location = pos*matrix
        else:
            print("Could not find", prm_name)


######################################################
# IMPORT
######################################################
def load_fin(filepath, context, matrix):

    print("importing fin: %r..." % (filepath))

    time1 = time.clock()


    # start reading the fin file
    load_fin_file(filepath, matrix)

    print(" done in %.4f sec." % (time.clock() - time1))



def load(operator, filepath, context, matrix):

    global export_filename
    export_filename = filepath

    load_fin(filepath, context, matrix)

    return {'FINISHED'}
