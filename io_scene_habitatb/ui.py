# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import bpy
import bmesh
import mathutils
from . import helpers, const

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        CollectionProperty,
        )

flag_names = ["Double-Sided", "Transparent", "Alpha or Additive", "No EnvMap", "EnvMap"]
flag_descr = ["Set to make the polygon visible from both sides.", 
            "Set to enable transparency for this polygon. Re-Volt will then apply transparency from the texture and the alpha vertex color channel.", 
            "Set to make Re-Volt render this polygon with alpha transparency from the texture or use additive blending (dark colors become transparent, brighter colors lighten/glow).",
            "Set to disable the environment map (don't make the polygon shiny, e.g. for the underside of cars)." 
            "Set to enable the environment map (make the polygon shiny)."]


flags = [0x002, 0x004, 0x100, 0x200, 0x400, 0x800]


prop_states = [0, 0, 0, 0, 0, 0]

# class UIProperties(bpy.types.PropertyGroup):
#     rv_type = bpy.props.EnumProperty(
#         items = None, update = lambda self, context: set_rv_type(self, context, 'rv_type')
#     )

# main panel for selecting the object type
class RevoltTypePanel(bpy.types.Panel):
    bl_label = "Re-Volt Object Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        self.layout.prop(context.object.revolt, "rv_type")
        rvtype = context.object.revolt.rv_type
        if rvtype == "OBJECT":
            self.layout.prop(context.object.revolt, "object_type", text="Object Type")
            self.layout.prop(context.object.revolt, "flag1_long", text="Setting 1")
            self.layout.prop(context.object.revolt, "flag2_long", text="Setting 2")
            self.layout.prop(context.object.revolt, "flag3_long", text="Setting 3")
            self.layout.prop(context.object.revolt, "flag4_long", text="Setting 4")
        self.layout.label(text="Level Export:")
        # self.layout.prop(context.object.revolt, "export_as_prm") makes no sense to have
        if rvtype in ["OBJECT", "WORLD", "MESH", "NONE", "INSTANCE", "NCP"]:
            self.layout.prop(context.object.revolt, "export_as_w")
        
        if rvtype in ["OBJECT", "WORLD", "MESH", "NONE", "INSTANCE"]:
            self.layout.prop(context.object.revolt, "export_as_ncp")
            self.layout.prop(context.object.revolt, "use_tex_num")



class RevoltFacePropertiesPanel(bpy.types.Panel):
    bl_label = "Re-Volt Face Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"
    
    selection = None
    selected_face_count = None

    # @classmethod
    # def poll(self, context):
    #     return context.object.type == "MESH"
    
    def draw(self, context):
        obj = context.object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        flags = bm.faces.layers.int.get("flags") or bm.faces.layers.int.new("flags")
        texture = bm.faces.layers.int.get("texture") or bm.faces.layers.int.new("texture")
        if self.selected_face_count is None or self.selected_face_count != mesh.total_face_sel:
            self.selected_face_count = mesh.total_face_sel
            self.selection = [face for face in bm.faces if face.select]
        
        # count the number of faces the flags are set for
        count = [0] * len(const.FACE_PROPS)
        # if len(self.selection) > 1:            
        for face in self.selection:
            for x in range(len(const.FACE_PROPS)):
                if face[flags] & const.FACE_PROPS[x]:
                    count[x] += 1


        rvtype = context.object.revolt.rv_type
        if rvtype in ["NCP"]:
            self.layout.prop(context.object.data.revolt, "face_material", text="Material".format(""))
        if rvtype in ["MESH", "WORLD", "OBJECT", "INSTANCE"]:
                
            self.layout.prop(context.object.data.revolt, "face_double_sided", text="{}: Double sided".format(count[1]))
            self.layout.prop(context.object.data.revolt, "face_translucent", text="{}: Translucent".format(count[2]))
            self.layout.prop(context.object.data.revolt, "face_mirror", text="{}: Mirror".format(count[3]))
            self.layout.prop(context.object.data.revolt, "face_additive", text="{}: Additive blending".format(count[4]))
            self.layout.prop(context.object.data.revolt, "face_texture_animation", text="{}: Texture animation".format(count[5]))
            self.layout.prop(context.object.data.revolt, "face_no_envmapping", text="{}: No EnvMap".format(count[6]))
            self.layout.prop(context.object.data.revolt, "face_envmapping", text="{}: EnvMap".format(count[7]))
            self.layout.prop(context.object.data.revolt, "face_cloth", text="{}: Cloth effect".format(count[8]))
            self.layout.prop(context.object.data.revolt, "face_skip", text="{}: Do not export".format(count[9]))
            if len(self.selection) > 1:
                self.layout.prop(context.object.data.revolt, "face_texture", text="Texture (multiple)")
                self.layout.label(text="(Texture will be applied to all selected faces.)")
            else:
                self.layout.prop(context.object.data.revolt, "face_texture", text="Texture".format(""))
        else:
            self.layout.label(text="Face properties are")
            self.layout.label(text="only available for Mesh,")
            self.layout.label(text="World, Object and")
            self.layout.label(text="Instance types.")
# panel for setting vertex colors
class RevoltVertexPanel(bpy.types.Panel):
    bl_label = "HabitatB Vertex Colors"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"

    selection = None
    selected_face_count = None

    def draw(self, context):
        obj = context.object
        row = self.layout.row(align=True)
        if context.mode != "EDIT_MESH":
            row = self.layout.row()
            row.label(text="Please enable Edit Mode to edit vertex colors.", icon='INFO')
        else:
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            vc_layer = bm.loops.layers.color.get("color")
           
            # update selection data
            if self.selected_face_count is None or self.selected_face_count != mesh.total_face_sel:
                self.selected_face_count = mesh.total_face_sel
                self.selection = [face for face in bm.faces if face.select]
        
            if vc_layer is None:
                row = self.layout.row()
                row.label(text="Please create a vertex color layer.", icon='INFO')
                row = self.layout.row()
                row.operator("vertexcolor.create_layer", icon='PLUS')

            elif self.selection:
                row = self.layout.row()
                row.operator("vertexcolor.set", text="Grey 50%").number=50
                row.operator("vertexcolor.set", text="")
                row = self.layout.row()
                col = row.column(align=True)
                col.alignment = 'EXPAND'
                col.operator("vertexcolor.set", text="Grey 45%").number=45
                col.operator("vertexcolor.set", text="Grey 40%").number=40
                col.operator("vertexcolor.set", text="Grey 35%").number=35
                col.operator("vertexcolor.set", text="Grey 30%").number=30
                col.operator("vertexcolor.set", text="Grey 20%").number=20
                col.operator("vertexcolor.set", text="Grey 10%").number=10
                col.operator("vertexcolor.set", text="Black").number=0
                col = row.column(align=True)
                col.alignment = 'EXPAND'
                col.operator("vertexcolor.set", text="Grey 55%").number=55
                col.operator("vertexcolor.set", text="Grey 60%").number=60
                col.operator("vertexcolor.set", text="Grey 65%").number=65
                col.operator("vertexcolor.set", text="Grey 70%").number=70
                col.operator("vertexcolor.set", text="Grey 80%").number=80
                col.operator("vertexcolor.set", text="Grey 90%").number=90
                col.operator("vertexcolor.set", text="White").number=100


class RevoltToolPanel(bpy.types.Panel):
    bl_label = "Re-Volt Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    # bl_context = "mesh_edit"
    bl_category = "Re-Volt"
    def draw(self, context):
        obj = context.object
        self.layout.label(text="Type: "+obj.revolt.rv_type)
        
        if context.mode == "OBJECT":
            row = self.layout.row()
            self.layout.label(text="Set all selected objects to...")
            row = self.layout.row()
            row.operator("objtype.setw", text="World")
            row.operator("objtype.setprm", text="PRM")
            row.operator("objtype.setncp", text="NCP")
        
        if context.mode == "EDIT_MESH":
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            
            vc_layer = bm.loops.layers.color.get("color")
            alpha_layer = bm.loops.layers.color.get("alpha")

            
            if vc_layer is None:
                row = self.layout.row()
                row.operator("vertexcolor.create_layer", icon='PLUS')
            if alpha_layer is None:
                row = self.layout.row()
                row.operator("alphacolor.create_layer", icon='PLUS')



# BUTTONS

class ButtonSetAllW(bpy.types.Operator):
    bl_idname = "objtype.setw"
    bl_label = "Set all selected objects to World."
 
    def execute(self, context):
        set_all_w(context)
        return{'FINISHED'} 

class ButtonSetAllPRM(bpy.types.Operator):
    bl_idname = "objtype.setprm"
    bl_label = "Set all selected objects to World."
 
    def execute(self, context):
        set_all_prm(context)
        return{'FINISHED'} 

class ButtonSetAllNCP(bpy.types.Operator):
    bl_idname = "objtype.setncp"
    bl_label = "Set all selected objects to World."
 
    def execute(self, context):
        set_all_ncp(context)
        return{'FINISHED'} 

class ButtonVertexColorSet(bpy.types.Operator):
    bl_idname = "vertexcolor.set"
    bl_label = "SET COLOR"
    number = bpy.props.IntProperty()
 
    def execute(self, context):
        set_vertex_color(context, self.number)
        return{'FINISHED'}    

class ButtonVertexColorCreateLayer(bpy.types.Operator):
    bl_idname = "vertexcolor.create_layer"
    bl_label = "Create vertex color layer"
 
    def execute(self, context):
        create_color_layer(context)
        return{'FINISHED'} 

class ButtonVertexColorCreateLayer(bpy.types.Operator):
    bl_idname = "alphacolor.create_layer"
    bl_label = "Create alpha color layer"
 
    def execute(self, context):
        create_alpha_layer(context)
        return{'FINISHED'} 
 

# BUTTON FUNCTIONS

def set_vertex_color(context, number):
    print(context, number)
    bm = bmesh.from_edit_mesh(context.object.data)        
    verts = [ v for v in bm.verts if v.select ]
    if verts:
        colors = bm.loops.layers.color.get("color")   
        for v in verts:
            for loop in v.link_loops:
                loop[colors] = mathutils.Color((number/100, number/100, number/100))
                
        bmesh.update_edit_mesh(context.object.data)

def set_all_w(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.rv_type = "WORLD"
def set_all_prm(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.rv_type = "MESH"
def set_all_ncp(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.rv_type = "NCP"



def create_color_layer(context):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.loops.layers.color.new("color")

def create_alpha_layer(context):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.loops.layers.color.new("alpha")