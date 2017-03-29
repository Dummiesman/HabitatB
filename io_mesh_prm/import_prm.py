# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

import bpy, bmesh, mathutils
import time, struct

export_filename = None

######################################################
# IMPORT MAIN FILES
######################################################
def load_prm_file(file):
    scn = bpy.context.scene
    
    # get mesh name
    mesh_name = bpy.path.basename(export_filename)
    
    # add a mesh and link it to the scene
    me = bpy.data.meshes.new(mesh_name)
    ob = bpy.data.objects.new(mesh_name, me)

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(me)

    # create layers
    uv_layer = bm.loops.layers.uv.new()    
    vc_layer = bm.loops.layers.color.new()
    
    scn.objects.link(ob)
    scn.objects.active = ob
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    # read prm header
    poly_count, vertex_count = struct.unpack('<HH', file.read(4))
    poly_offset = file.tell()
    
    # skip polys real quick
    file.seek(60 * poly_count, 1)
    
    # read vertices
    print("reading verts at " + str(file.tell()))
    for vert in range(vertex_count):
      location = struct.unpack('fff', file.read(12))
      normal = struct.unpack('fff', file.read(12))
      bm.verts.new((location[0] * 0.01, location[1] * 0.01, location[2] * 0.01)) # RV units are giant!!
    
    # ensure lookup table before continuing
    bm.verts.ensure_lookup_table()
    
    # read faces
    file.seek(poly_offset, 0)
    for poly in range(poly_count):
      flags, texture = struct.unpack('<Hh', file.read(4))
      indices = struct.unpack('<HHHH', file.read(8))
      
      # check if we have a quad
      is_quad = (flags & 0x001)
      num_loops = 4 if is_quad else 3
      
      # faces are reversed also
      if is_quad:
        face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]], bm.verts[indices[3]]))
        face.smooth = True
      else:
        face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]])) 
        face.smooth = True
      
      # read colors and uvs
      colors = struct.unpack('<BBBBBBBBBBBBBBBB', file.read(16))
      uvs = struct.unpack('ffffffff', file.read(32))
      
      # set uvs
      for uv_set_loop in range(num_loops):
        uv = (uvs[uv_set_loop * 2], 1 - uvs[uv_set_loop * 2 + 1])
        face.loops[uv_set_loop][uv_layer].uv = uv
        
      # set colors
      for color_set_loop in range(num_loops):
        color_idx = color_set_loop * 4
        color_r = float(colors[color_idx] + 1) / 255
        color_g = float(colors[color_idx] + 2) / 255
        color_b = float(colors[color_idx] + 3) / 255
        color_a = float(colors[color_idx] + 4) / 255
        
        face.loops[color_set_loop][vc_layer] = mathutils.Color((color_r, color_g, color_b))

      # tag faces  with flags
      #face.tag = flags
      
    # calculate normals
    bm.normal_update()
    
    # free resources
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)
    bm.free()
      

######################################################
# IMPORT
######################################################
def load_prm(filepath,
             context):

    print("importing PRM: %r..." % (filepath))

    time1 = time.clock()
    file = open(filepath, 'rb')

    # start reading our pkg file
    load_prm_file(file)

    print(" done in %.4f sec." % (time.clock() - time1))
    file.close()


def load(operator,
         context,
         filepath="",
         ):

    global export_filename
    export_filename = filepath
    
    load_prm(filepath,
             context,
             )

    return {'FINISHED'}
