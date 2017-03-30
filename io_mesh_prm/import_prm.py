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

    # create layers and set names
    uv_layer = bm.loops.layers.uv.new("uv")    
    vc_layer = bm.loops.layers.color.new("color")
    va_layer = bm.loops.layers.color.new("alpha")
    flag_layer = bm.faces.layers.int.new("flags")
    
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
      bm.verts.new((location[0] * 0.01, location[2] * 0.01, location[1] * -0.01)) # RV units are giant!!
    
    # ensure lookup table before continuing
    bm.verts.ensure_lookup_table()
    
    # read faces
    file.seek(poly_offset, 0)
    for poly in range(poly_count):
      flags, texture = struct.unpack('<Hh', file.read(4))
      indices = struct.unpack('<HHHH', file.read(8))
      
      # read colors and uvs
      colors = struct.unpack('<BBBBBBBBBBBBBBBB', file.read(16))
      uvs = struct.unpack('ffffffff', file.read(32))
      
      # check if we have a quad
      is_quad = (flags & 0x001)
      num_loops = 4 if is_quad else 3

      # is this quad actually a triangle?
      if is_quad and len(set(indices)) == 3:
        is_quad = False

      # check if it's a valid face
      if len(set(indices)) > 2:
        existing_face = bm.faces.get([bm.verts[i] for i in (indices if is_quad else indices[:3])])

        # faces are reversed also
        try:
          if is_quad:
            face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]], bm.verts[indices[3]]))
            face.smooth = True
          else:
            face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]])) 
            face.smooth = True

          for loop in range(num_loops):
            # set uvs
            uv = (uvs[loop * 2], 1 - uvs[loop * 2 + 1])
            face.loops[loop][uv_layer].uv = uv
            
            # set colors
            color_idx = loop * 4
            color_b = float(colors[color_idx]) / 255
            color_g = float(colors[color_idx + 1]) / 255
            color_r = float(colors[color_idx + 2]) / 255
            color_a = float(colors[color_idx + 3]) / 255
            
            # apply colors and alpha to layers
            face.loops[loop][vc_layer] = mathutils.Color((color_r, color_g, color_b))
            face.loops[loop][va_layer] = mathutils.Color((color_a, color_a, color_a))
            face[flag_layer] = flags
        except ValueError as e:
          print(e)
          # set existing face as double-sided
          existing_face[flag_layer] |= 0x002
        
        # flip normals
        face.normal_flip()
        
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
