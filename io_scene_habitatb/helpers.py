# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import mathutils
import struct

scale = 10.0

NCP_QUAD = 1
NCP_TWOSIDED = 2
NCP_OBJECT_ONLY = 4
NCP_CAMERA_ONLY = 8
NCP_NON_PLANAR = 16
NCP_NO_SKID = 32
NCP_OIL = 64

def vc_to_bitfield(color_layer):
    flags_b0 = int(color_layer[0] * 255.0)
    flags_b1 = int(color_layer[2] * 255.0)
    flags_ba = bytearray([flags_b0, flags_b1])
    flags_int = int.from_bytes(flags_ba, byteorder='little', signed=False)
    return flags_int

def bitfield_to_vc(number):
    flags_bytes = number.to_bytes(2, byteorder='little', signed=False)
    flagR = float(flags_bytes[0]) / 255.0
    flagB = float(flags_bytes[1]) / 255.0
    return mathutils.Color((flagR, 1.0, flagB))

def get_flag_long(self, start):
    return struct.unpack("=l", bytes(self.flags[start:start + 4]))[0]

def set_flag_long(self, value, start):
    for i,b in enumerate(struct.pack("=l", value), start):
        self.flags[i] = b

def get_intersection(d1, n1, d2, n2, d3, n3):
    den = n1.dot(n1.cross(n3))
    if abs(den) < 1e-100:
        print("No intersection.")
        return None
    return (d1 * n1.cross(n3) + d2 * n3.cross(n1) + d3 * n1.cross(n1)) / den

def to_blender_scale(val):
    return val / scale

def to_blender_axis(val):
    return (val[0], val[2], -val[1])