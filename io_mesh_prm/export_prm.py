# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

import os, time, struct, math, sys
import os.path as path

import bpy, bmesh, mathutils


######################################################
# EXPORT HELPERS
######################################################

######################################################
# EXPORT MAIN FILES
######################################################

def save_prm_file(file, ob):
    scn = bpy.context.scene
    
    # get mesh name
    mesh = ob.data

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    faces = list(bm.faces)
    vertices = list(bm.verts)

    poly_count = len(faces)
    vertex_count = len(vertices)

    # write amount of polygons and vertices
    file.write(struct.pack("<hh", poly_count, vertex_count))

    # get layers
    uv_layer = bm.loops.layers.uv.active
    vc_layer = bm.loops.layers.color.get("color")
    va_layer = bm.loops.layers.color.get("alpha")
    flag_layer = bm.loops.layers.int.get("flags")

    for poly in range(poly_count):

      face = faces[poly]

      is_quad = 1 if len(face.verts) > 3 else 0
      try:
        bitfield = face.loops[poly][flag_layer]
      except:
        bitfield = 0

      if is_quad:
        bitfield |= 0x001

      # write the flags
      file.write(struct.pack("<h", bitfield))

      # write the texture
      file.write(struct.pack("<h", 0))

      # write the vertex indices
      vert_order = [2, 1, 0, 3] if len(face.verts) < 4 else [3, 2, 1, 0]
      for i in vert_order:
        if i < len(face.verts):
          file.write(struct.pack("<h", vertices.index(face.verts[i])))
        else:
          file.write(struct.pack("<h", 0))

      # write the vertex colors
      for i in vert_order:
        if i < len(face.verts):
          color = face.loops[i][vc_layer]
          alpha = face.loops[i][va_layer]

          file.write(struct.pack("<BBBB", int(color.r * 255), int(color.g * 255), int(color.b * 255), int(alpha.v * 255)))
        else:
          file.write(struct.pack("<BBBB", 0, 0, 0, 0))

      # write the uv
      for i in vert_order:
        if i < len(face.verts):
          uv = face.loops[i][uv_layer].uv
          file.write(struct.pack("<ff", uv[0], 1 - uv[1]))
        else:
          file.write(struct.pack("<ff", 0, 0))


      for vertex in range(vertex_count):
        v = vertices[vertex]
        coord = mathutils.Vector((v.co[0]*100, v.co[2]*100, v.co[1]*-100))
        file.write(struct.pack("<fff", coord[0], coord[1], coord[2]))
        file.write(struct.pack("<fff", coord[0], coord[1], coord[2]))

    bm.free()



######################################################
# EXPORT
######################################################
def save_prm(filepath,
             context):


    time1 = time.clock()

    ob = bpy.context.selected_objects[0]
    print("exporting PRM: {} as {}...".format(str(ob), filepath))

    # write prm
    file = open(filepath, 'wb')
    save_prm_file(file, ob)
    file.close()

      
    # bound export complete
    print(" done in %.4f sec." % (time.clock() - time1))


def save(operator,
         context,
         filepath="",

         ):
  
    
    # save BND
    save_prm(filepath,
             context
             )

    return {'FINISHED'}