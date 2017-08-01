
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
from mathutils import Vector, Color

from . import const, parameters, import_prm

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
        name = struct.unpack('<9s', file.read(9))[0]
        name = str(name, encoding='ascii').split('\x00', 1)[0]

        # get the model color
        red, green, blue = struct.unpack('<3B', file.read(3))
        print(red, green, blue)
        # get the env color of the instance
        blue, green, red, alpha = struct.unpack('<BBBB', file.read(4))
        print(red, green, blue, alpha)

        # other props
        priority, flag = struct.unpack('<BBxx', file.read(4))
        lod_bias = struct.unpack('<f', file.read(4))[0]
        pos = Vector(struct.unpack("<3f", file.read(12)))
        rot_matrix = struct.unpack('<9f', file.read(36))

        if "{}.prm".format(name.lower()) in os.listdir(folder):
            infstance_path = os.sep.join([folder, "{}.prm".format(name.lower())])
            import_prm.load_prm(infstance_path, context, matrix)

        # inst_obj = bpy.data.objects.new(name, None)
        # bpy.context.scene.objects.link(inst_obj)
        context.object.location = pos*matrix



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
