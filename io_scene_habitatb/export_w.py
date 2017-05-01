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

import bpy, bmesh, mathutils
from mathutils import Color, Vector
from . import helpers, const


######################################################
# EXPORT MAIN FILES
######################################################

def save_w_file(file, matrix):
    scn = bpy.context.scene

    export_objs = []
    for obj in scn.objects:
        if obj.revolt.rv_type == "WORLD":
            export_objs.append(obj)

    # write the amount of meshes
    file.write(struct.pack("<l", len(export_objs)))

    # big mesh for writing the big ball
    big_mesh = bmesh.new()
    
    for ob in export_objs:
        # get mesh name
        mesh = ob.data

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # add to big mesh
        big_mesh.from_mesh(mesh)

        c = Vector(ob.location) * matrix
        r = max([helpers.get_distance(Vector(v.co) * matrix, c) for v in bm.verts])
        file.write(struct.pack("ffff", c[0], c[1], c[2], r))

        p1 = Vector([min([v.co.x for v in bm.verts]), min([v.co.y for v in bm.verts]), min([v.co.z for v in bm.verts])]) * matrix
        p2 = Vector([max([v.co.x for v in bm.verts]), max([v.co.y for v in bm.verts]), max([v.co.z for v in bm.verts])]) * matrix

        # # write bound balls
        # file.write(struct.pack("<3f", 0,0,0))
        # file.write(struct.pack("<f", 0.0))

        # write bbox
        file.write(struct.pack("<6f", p1[0], p1[1], p2[2], p2[0], p2[1], p2[2]))

        # write amount of polygons and vertices
        poly_count = len(bm.faces)
        vertex_count = len(bm.verts)
        file.write(struct.pack("<hh", poly_count, vertex_count))

        # get layers
        uv_layer = bm.loops.layers.uv.active
        vc_layer = bm.loops.layers.color.get("color")
        va_layer = bm.loops.layers.color.get("alpha")
        flag_layer = bm.faces.layers.int.get("flags") or bm.faces.layers.int.new("flags")
        texture_layer = bm.faces.layers.int.get("texture")
        texturefile_layer = bm.faces.layers.tex.active or bm.faces.layers.tex.new("texfile")


        # go through all polygons
        for face in bm.faces:
            # get flags 
            # figure out whether the face is quad
            is_quad = len(face.verts) > 3
        

            # set the quad-flag if the poly is quadratic
            if is_quad:
                face[flag_layer] |= const.FACE_QUAD

            # write the flags
            flags = face[flag_layer] if flag_layer else 0
            file.write(struct.pack("<H", flags))

            # write the texture
            if face[texturefile_layer].image:
                texnum = helpers.texture_to_int(face[texturefile_layer].image.name)
            elif texture_layer:
                texnum = face[texture_layer]
            else:
                texnum = -1
            
            file.write(struct.pack("<h", texnum))

            # get vertex order
            vert_order = [2, 1, 0, 3] if not is_quad else [3, 2, 1, 0]

            # write indices
            for i in vert_order:
                if i < len(face.verts):
                    file.write(struct.pack("<H", face.verts[i].index))
                else:
                    file.write(struct.pack("<H", 0))

            # write the vertex colors
            for i in vert_order:
                if i < len(face.verts):
                    # get color from the channel or fall back to a default valueCA
                    color = face.loops[i][vc_layer] if vc_layer else Color((1, 1, 1))
                    alpha = face.loops[i][va_layer] if va_layer else Color((1, 1, 1))
                    file.write(struct.pack("<BBBB", int(color.b * 255), int(color.g * 255), int(color.r * 255), int((alpha.v) * 255)))
                else:
                    file.write(struct.pack("<BBBB", 1, 1, 1, 1)) # write opaque white as default

            # write the uv
            for i in vert_order:
                if i < len(face.verts) and uv_layer:
                    uv = face.loops[i][uv_layer].uv
                    file.write(struct.pack("<ff", uv[0], 1 - uv[1]))
                else:
                    file.write(struct.pack("<ff", 0, 0))

        # export vertex positions and normals
        for vertex in bm.verts:
            coord = Vector((vertex.co[0] + ob.location.x, vertex.co[1] + ob.location.y, vertex.co[2] + ob.location.z)) * matrix
            normal = Vector((vertex.normal[0], vertex.normal[1], vertex.normal[2])) * matrix
            file.write(struct.pack("<fff", *coord))
            file.write(struct.pack("<fff", *normal))

        # free the bmesh
        bm.free()

    # write a bounding box surrounding the whole level
    p1 = Vector([min([v.co.x for v in big_mesh.verts]), min([v.co.y for v in big_mesh.verts]), min([v.co.z for v in big_mesh.verts])]) * matrix
    p2 = Vector([max([v.co.x for v in big_mesh.verts]), max([v.co.y for v in big_mesh.verts]), max([v.co.z for v in big_mesh.verts])]) * matrix
    file.write(struct.pack("<lffff", 1, (p1.x + p2.x) / 2, (p1.y + p2.y) / 2, (p1.z + p2.z) / 2, helpers.get_distance(p1, p2) / 2))
    file.write(struct.pack("<l", len(export_objs)))
    for i in range(len(export_objs)):
        file.write(struct.pack("<l", i))
    
    # no texture animations today
    file.write(struct.pack("<l", 0))

    big_mesh.free()


######################################################
# EXPORT
######################################################
def save_w(filepath, context, matrix):
             
    time1 = time.clock()

    # print("exporting W: {} as {}...".format(str(ob), filepath))

    # write the actual data
    file = open(filepath, 'wb')
    save_w_file(file, matrix)
    file.close()
     
    # prm export complete
    print(" done in %.4f sec." % (time.clock() - time1))


def save(operator, filepath, context, matrix):
    
    # save PRM file
    save_w(filepath, context, matrix)

    return {'FINISHED'}