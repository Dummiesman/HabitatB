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

def load_parameter_file(file, matrix):
    scn = bpy.context.scene
    params = parameters.read_parameters(file)

    return params


######################################################
# IMPORT
######################################################
def load_car(filepath, context, matrix):

    print("importing car: %r..." % (filepath))

    time1 = time.clock()

    # read the param file
    params = load_parameter_file(filepath, matrix)
    body = params["model {}".format(params["body"]["modelnum"])]

    wheel0loc = Vector(params["wheel 0"]["offset1"]) * matrix
    wheel1loc = Vector(params["wheel 1"]["offset1"]) * matrix
    wheel2loc = Vector(params["wheel 2"]["offset1"]) * matrix
    wheel3loc = Vector(params["wheel 3"]["offset1"]) * matrix

    folder = os.sep.join(filepath.split(os.sep)[:-1])
    
    wheel0_modelnum = int(params["wheel 0"]["modelnum"])
    if wheel0_modelnum >= 0:
        wheel0 = params["model {}".format(wheel0_modelnum)]
        if wheel0.split(os.sep)[-1] in os.listdir(folder):
                wheel0path = os.sep.join([folder, wheel0.split(os.sep)[-1]])
    else:
        wheel0 = None

    wheel1_modelnum = int(params["wheel 1"]["modelnum"])
    if wheel1_modelnum >= 0:
        wheel1 = params["model {}".format(wheel1_modelnum)]
        if wheel1.split(os.sep)[-1] in os.listdir(folder):
                wheel1path = os.sep.join([folder, wheel1.split(os.sep)[-1]])
    else:
        wheel1 = None

    wheel2_modelnum = int(params["wheel 2"]["modelnum"])
    if wheel2_modelnum >= 0:
        wheel2 = params["model {}".format(wheel2_modelnum)]
        if wheel2.split(os.sep)[-1] in os.listdir(folder):
                wheel2path = os.sep.join([folder, wheel2.split(os.sep)[-1]])
    else:
        wheel2 = None

    wheel3_modelnum = int(params["wheel 3"]["modelnum"])
    if wheel3_modelnum >= 0:
        wheel3 = params["model {}".format(wheel3_modelnum)]
        if wheel3.split(os.sep)[-1] in os.listdir(folder):
                wheel3path = os.sep.join([folder, wheel3.split(os.sep)[-1]])
    else:
        wheel3 = None


    # check if body is in the same folder
    if body.split(os.sep)[-1] in os.listdir(folder):
        bodypath = os.sep.join([folder, body.split(os.sep)[-1]])

    import_prm.load_prm(bodypath, context, matrix)
    body_obj = context.object

    if wheel0:
        import_prm.load_prm(wheel0path, context, matrix)
    else:
        wheel = bpy.data.objects.new("wheel 0", None)
        bpy.context.scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
        bpy.context.scene.objects.active = wheel
    context.object.location = wheel0loc
    context.object.parent = body_obj

    if wheel1:
        import_prm.load_prm(wheel1path, context, matrix)
    else:
        wheel = bpy.data.objects.new("wheel 1", None)
        bpy.context.scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
        bpy.context.scene.objects.active = wheel
    context.object.location = wheel1loc
    context.object.parent = body_obj

    if wheel2:
        import_prm.load_prm(wheel2path, context, matrix)
    else:
        wheel = bpy.data.objects.new("wheel 2", None)
        bpy.context.scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
        bpy.context.scene.objects.active = wheel
    context.object.location = wheel2loc
    context.object.parent = body_obj

    if wheel3:
        import_prm.load_prm(wheel3path, context, matrix)
    else:
        wheel = bpy.data.objects.new("wheel 3", None)
        bpy.context.scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
        bpy.context.scene.objects.active = wheel
    context.object.location = wheel3loc
    context.object.parent = body_obj

    print(" done in %.4f sec." % (time.clock() - time1))


def load(operator, filepath, context, matrix):

    global export_filename
    export_filename = filepath

    load_car(filepath, context, matrix)

    return {'FINISHED'}
