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
import bpy
import bmesh

scale = 10.0

NCP_QUAD = 1
NCP_TWOSIDED = 2
NCP_OBJECT_ONLY = 4
NCP_CAMERA_ONLY = 8
NCP_NON_PLANAR = 16
NCP_NO_SKID = 32
NCP_OIL = 64


materials = [
    ("MATERIAL_NONE", "None", "None", "", -1),
    ("MATERIAL_DEFAULT", "Default", "None", "", 0),
    ("MATERIAL_MARBLE", "Marble", "None", "", 1),
    ("MATERIAL_STONE", "Stone", "None", "", 2),
    ("MATERIAL_WOOD", "Wood", "None", "", 3),
    ("MATERIAL_SAND", "Sand", "None", "", 4),
    ("MATERIAL_PLASTIC", "Plastic", "None", "", 5),
    ("MATERIAL_CARPETTILE", "Carpet tile", "None", "", 6),
    ("MATERIAL_CARPETSHAG", "Carpet shag", "None", "", 7),
    ("MATERIAL_BOUNDARY", "Boundary", "None", "", 8),
    ("MATERIAL_GLASS", "Glass", "None", "", 9),
    ("MATERIAL_ICE1", "Ice 1", "None", "", 10),
    ("MATERIAL_METAL", "Metal", "None", "", 11),
    ("MATERIAL_GRASS", "Grass", "None", "", 12),
    ("MATERIAL_BUMPMETAL", "Bump metal", "None", "", 13),
    ("MATERIAL_PEBBLES", "Pebbles", "None", "", 14),
    ("MATERIAL_GRAVEL", "Gravel", "None", "", 15),
    ("MATERIAL_CONVEYOR1", "Conveyor 1", "None", "", 16),
    ("MATERIAL_CONVEYOR2", "Conveyor 2", "None", "", 17),
    ("MATERIAL_DIRT1", "Dirt 1", "None", "", 18),
    ("MATERIAL_DIRT2", "Dirt 2", "None", "", 19),
    ("MATERIAL_DIRT3", "Dirt 3", "None", "", 20),
    ("MATERIAL_ICE2", "Ice 2", "None", "", 21),
    ("MATERIAL_ICE3", "Ice 3", "None", "", 22)
    ]

def get_face_material(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0 or any([face[layer] != selected_faces[0][layer] for face in selected_faces]):
        return -1
    else:
        return selected_faces[0][layer]

def set_face_material(self, value):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    for face in bm.faces:
        if face.select:
            face[layer] = value

def get_face_texture(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("texture") or bm.faces.layers.int.new("texture")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0 or any([face[layer] != selected_faces[0][layer] for face in selected_faces]):
        return -1
    else:
        return selected_faces[0][layer]

def set_face_texture(self, value):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("texture") or bm.faces.layers.int.new("texture")
    for face in bm.faces:
        if face.select:
            face[layer] = value

def get_face_property(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_face_type") or bm.faces.layers.int.new("revolt_face_type")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0:
        return 0
    output = selected_faces[0][layer]
    for face in selected_faces:
        output = output & face[layer]
    return output
            
def set_face_property(self, value, mask):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_face_type") or bm.faces.layers.int.new("revolt_face_type")
    for face in bm.faces:
        if face.select:
            # for arg in args:
            face[layer] = face[layer] | mask if value else face[layer] & ~mask

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