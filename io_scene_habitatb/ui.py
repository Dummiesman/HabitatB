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
from math import pi
from . import helpers, const, io_ops, tools

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
        if rvtype == "INSTANCE":
            row = self.layout.row(align=True)
            row.prop(context.object.revolt, "fin_flag_model_rgb", text="Model Color")
            row.prop(context.object.revolt, "fin_col", text="")
            row = self.layout.row(align=True)
            row.prop(context.object.revolt, "fin_flag_env", text="EnvColor")
            row.prop(context.object.revolt, "fin_envcol", text="")
            self.layout.prop(context.object.revolt, "fin_flag_hide")
            self.layout.prop(context.object.revolt, "fin_flag_no_mirror")
            self.layout.prop(context.object.revolt, "fin_flag_no_lights")
            self.layout.prop(context.object.revolt, "fin_flag_no_camera_coll")
            self.layout.prop(context.object.revolt, "fin_flag_no_object_coll")
            self.layout.prop(context.object.revolt, "fin_priority")
            self.layout.prop(context.object.revolt, "fin_lod_bias")

        box = self.layout.box()
        box.label(text="Additionally export as:")
        # self.layout.prop(context.object.revolt, "export_as_prm") makes no sense to have
        if rvtype in ["OBJECT", "WORLD", "MESH", "NONE", "INSTANCE", "NCP"]:
            box.prop(context.object.revolt, "export_as_w", text="W (World)")

        if rvtype in ["OBJECT", "WORLD", "MESH", "NONE", "INSTANCE"]:
            box.prop(context.object.revolt, "export_as_ncp", text="NPC (Collision)")

        box.label(text="Other Properties:")
        box.prop(context.object.revolt, "use_tex_num")

class RevoltFacePropertiesPanel(bpy.types.Panel):
    bl_label = "Face Properties"
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
        flags = bm.faces.layers.int.get("Flags") or bm.faces.layers.int.new("Flags")
        texture = bm.faces.layers.int.get("Texture") or bm.faces.layers.int.new("Texture")
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
        if rvtype in ["NCP"] or context.object.revolt.export_as_ncp:
            self.layout.prop(context.object.data.revolt, "face_material", text="Material".format(""))
        if rvtype in ["MESH", "WORLD", "OBJECT", "INSTANCE"]:
            row  = self.layout.row()
            col = row.column(align = True)
            col.prop(context.object.data.revolt, "face_double_sided", text="{}: Double sided".format(count[1]))
            col.prop(context.object.data.revolt, "face_translucent", text="{}: Translucent".format(count[2]))
            col.prop(context.object.data.revolt, "face_mirror", text="{}: Mirror".format(count[3]))
            col.prop(context.object.data.revolt, "face_additive", text="{}: Additive blending".format(count[4]))
            col.prop(context.object.data.revolt, "face_texture_animation", text="{}: Texture animation".format(count[5]))
            col.prop(context.object.data.revolt, "face_no_envmapping", text="{}: No EnvMap".format(count[6]))
            col.prop(context.object.data.revolt, "face_envmapping", text="{}: EnvMap".format(count[7]))
            col.prop(context.object.data.revolt, "face_cloth", text="{}: Cloth effect".format(count[8]))
            col.prop(context.object.data.revolt, "face_skip", text="{}: Do not export".format(count[9]))
            col = row.column(align=True)
            col.scale_x = 0.15
            col.operator("faceprops.select", text="sel").prop = const.FACE_DOUBLE
            col.operator("faceprops.select", text="sel").prop = const.FACE_TRANSLUCENT
            col.operator("faceprops.select", text="sel").prop = const.FACE_MIRROR
            col.operator("faceprops.select", text="sel").prop = const.FACE_TRANSL_TYPE
            col.operator("faceprops.select", text="sel").prop = const.FACE_TEXANIM
            col.operator("faceprops.select", text="sel").prop = const.FACE_NOENV
            col.operator("faceprops.select", text="sel").prop = const.FACE_CLOTH
            col.operator("faceprops.select", text="sel").prop = const.FACE_CLOTH
            col.operator("faceprops.select", text="sel").prop = const.FACE_SKIP


            if len(self.selection) > 1:
                self.layout.prop(context.object.data.revolt, "face_texture", text="Texture (multiple)")
                self.layout.label(text="(Texture will be applied to all selected faces.)")
            else:
                self.layout.prop(context.object.data.revolt, "face_texture", text="Texture".format(""))
        else:
            self.layout.label(text="Assign a type first.", icon="INFO")

"""
Panel for setting vertex colors in Edit Mode.
If there is no vertex color layer, the user will be prompted to create one.
It includes buttons for setting vertex colors in different shades of grey and
a custom color which is chosen with a color picker.
"""
class RevoltVertexPanel(bpy.types.Panel):
    bl_label = "Vertex Colors"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"

    selection = None
    selected_face_count = None

    def draw(self, context):
        obj = context.object
        row = self.layout.row(align=True)

        # warn if texture mode is not enabled
        widget_texture_mode(self)

        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        vc_layer = bm.loops.layers.color.get("Col")

        # # update selection data
        # if self.selected_face_count is None or self.selected_face_count != mesh.total_face_sel:
        #     self.selected_face_count = mesh.total_face_sel
        #     self.selection = [face for face in bm.faces if face.select]

        if widget_vertex_color_channel(self, obj):
            pass # there is not vertex color channel and the panel can't be used

        else:
            box = self.layout.box()
            row = box.row()
            row.template_color_picker(context.object.revolt, 'vertex_color_picker', value_slider=True)

            row = box.row(align=True)
            row.prop(context.object.revolt, 'vertex_color_picker', text = '')
            row.operator("vertexcolor.set", text="Color").number=-1
            row = self.layout.row(align=True)
            row.operator("vertexcolor.set", text="Grey 50%").number=50
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

"""
Tool panel in the left sidebar of the viewport for performing
various operations
"""
class RevoltIOToolPanel(bpy.types.Panel):
    bl_label = "Import/Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"

    def draw(self, context):
        # i/o buttons
        # create a list with object types to later check if an export is possible
        types = helpers.get_object_types(context)

        box = self.layout.box()
        box.label(text="Import", icon="IMPORT")
        row = box.row(align=True)
        row.operator(io_ops.ImportPRM.bl_idname, text="PRM")
        row.operator(io_ops.ImportW.bl_idname, text="W")
        row.operator(io_ops.ImportNCP.bl_idname, text="NCP")
        row = box.row(align=True)
        row.operator(io_ops.ImportPOS.bl_idname, text="POS")
        row.operator(io_ops.ImportFIN.bl_idname, text="FIN")
        row = box.row(align=True)
        row.operator(io_ops.ImportCAR.bl_idname, text="Car (parameters.txt)")

        box = self.layout.box()
        box.label(text="Export", icon="EXPORT")
        row = box.row(align=True)
        if bpy.context.active_object:
            row.operator(io_ops.ExportPRM.bl_idname, text="PRM")
        else:
            row.operator(io_ops.ExportPRM.bl_idname, text="PRM", icon="X")

        if "WORLD" in types:
            row.operator(io_ops.ExportW.bl_idname, text="W")
        else:
            row.operator(io_ops.ExportW.bl_idname, text="W", icon="X")

        if "NCP" in types:
            row.operator(io_ops.ExportNCP.bl_idname, text="NCP")
        else:
            row.operator(io_ops.ExportNCP.bl_idname, text="NCP", icon="X")

"""
Tools for batch-setting common objects types and properties.
This is only visible in object mode (left tools panel).
"""
class RevoltOBJToolPanel(bpy.types.Panel):
    bl_label = "Object Types"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"

    def draw(self, context):

        if context.mode == "OBJECT":
            obj = context.object
            if not obj:
                return

            box = self.layout.box()
            # row.label(text="Type (active object): "+obj.revolt.rv_type)

            # !!! self.layout.prop(context.object.revolt, "rv_type")
            # !!! IMPORTANT: unlike props for faces, this would only set the type the selected/active object
            # !!! that's why we need the operator functions!

            box.label(text="Object type (for all selected):")
            row = box.row(align=True)
            row.operator("objtype.setw", text="World")
            row.operator("objtype.setprm", text="PRM")
            row.operator("objtype.setncp", text="NCP")

            # Batch buttons for setting additional export types
            box = self.layout.box()
            box.label(text="Additional export (for all selected):")
            row = box.row(align=True)
            row.operator("objtype.setalladdw", text="World")
            row.operator("objtype.unsetalladdw", text="Not World")
            row = box.row(align=True)
            row.operator("objtype.setalladdncp", text="NCP")
            row.operator("objtype.unsetalladdncp", text="Not NCP")


class RevoltLightPanel(bpy.types.Panel):
    bl_label = "Light and Shadow"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"

    def draw(self, context):
        view = context.space_data

        obj = context.object

        # warn if texture mode is not enabled
        widget_texture_mode(self)

        if obj and obj.select:

            # check if the object has a vertex color layer
            if widget_vertex_color_channel(self, obj):
                pass

            else:
                # light orientation selection
                box = self.layout.box()
                box.label(text="Shade Object")
                row = box.row()
                row.prop(context.object.revolt, "light_orientation", text="Orientation")
                if obj.revolt.light_orientation == "X":
                    dirs = ["Left", "Right"]
                if obj.revolt.light_orientation == "Y":
                    dirs = ["Front", "Back"]
                if obj.revolt.light_orientation == "Z":
                    dirs = ["Top", "Bottom"]
                # headings
                row = box.row()
                row.label(text="Direction")
                row.label(text="Light")
                row.label(text="Intensity")
                # settings for the first light
                row = box.row()
                row.label(text=dirs[0])
                row.prop(context.object.revolt, "light1", text="")
                row.prop(context.object.revolt, "light_intensity1", text="")
                # settings for the second light
                row = box.row()
                row.label(text=dirs[1])
                row.prop(context.object.revolt, "light2", text="")
                row.prop(context.object.revolt, "light_intensity2", text="")
                # bake button
                row = box.row()
                row.operator("lighttools.bakevertex", text="Generate Shading", icon="LIGHTPAINT")

            box = self.layout.box()
            box.label(text="Generate Shadow Texture")
            row = box.row()
            row.prop(context.object.revolt, "shadow_method")
            col = box.column(align=True)
            col.prop(context.object.revolt, "shadow_quality")
            col.prop(context.object.revolt, "shadow_softness")
            col.prop(context.object.revolt, "shadow_resolution")
            row = box.row()
            row.operator("lighttools.bakeshadow", icon="LAMP_SPOT", text="Generate Shadow")
            row = box.row()
            row.prop(context.object.revolt, "shadow_table", text="Table")

# WIDGETS
"""
Widgets are little panel snippets that generally warn users if something isn't
set up correctly to use a feature. They return true if something isn't right.
They return false if everything is alright.
"""

def widget_texture_mode(self):
    if not helpers.texture_mode_enabled():
        box = self.layout.box()
        box.label(text="Texture Mode is not enabled.", icon='INFO')
        row = box.row()
        row.operator("helpers.enable_texture_mode", text="Enable Texture Mode", icon="POTATO")
        return True
    return False

def widget_vertex_color_channel(self, obj):
    if not obj.data.vertex_colors:
        box = self.layout.box()
        box.label(text="No Vertex Color Layer.", icon='INFO')
        row = box.row()
        row.operator("mesh.vertex_color_add", icon='PLUS', text="Create Vertex Color Layer")
        return True
    return False

# BUTTONS

# SET OBJECT TYPE
class ButtonSetAllW(bpy.types.Operator):
    bl_idname = "objtype.setw"
    bl_label = "Set all selected objects to World."

    def execute(self, context):
        helpers.set_all_w(context)
        return{'FINISHED'}

class ButtonSetAllPRM(bpy.types.Operator):
    bl_idname = "objtype.setprm"
    bl_label = "Set all selected objects to PRM."

    def execute(self, context):
        helpers.set_all_prm(context)
        return{'FINISHED'}

class ButtonSetAllNCP(bpy.types.Operator):
    bl_idname = "objtype.setncp"
    bl_label = "Set all selected objects to NCP."

    def execute(self, context):
        helpers.set_all_ncp(context)
        return{'FINISHED'}
# FACE PROP SELECTORS

class ButtonSelectFaceProp(bpy.types.Operator):
    bl_idname = "faceprops.select"
    bl_label = "sel"
    prop = bpy.props.IntProperty()

    def execute(self, context):
        helpers.select_faces(context, self.prop)
        return{'FINISHED'}

# ADDITIONAL OBJECT TYPE

class ButtonSetAllAddW(bpy.types.Operator):
    bl_idname = "objtype.setalladdw"
    bl_label = "Set Additional export to selected objects."

    def execute(self, context):
        helpers.set_all_add_w(context)
        return{'FINISHED'}

class ButtonSetAllAddNCP(bpy.types.Operator):
    bl_idname = "objtype.setalladdncp"
    bl_label = "Set Additional export to selected objects."

    def execute(self, context):
        helpers.set_all_add_ncp(context)
        return{'FINISHED'}

# unset

class ButtonUnsetAllAddW(bpy.types.Operator):
    bl_idname = "objtype.unsetalladdw"
    bl_label = "Unset Additional export to selected objects."

    def execute(self, context):
        helpers.unset_all_add_w(context)
        return{'FINISHED'}

class ButtonUnsetAllAddNCP(bpy.types.Operator):
    bl_idname = "objtype.unsetalladdncp"
    bl_label = "Unset Additional export to selected objects."

    def execute(self, context):
        helpers.unset_all_add_ncp(context)
        return{'FINISHED'}

# VERTEX COLORS

class ButtonVertexColorSet(bpy.types.Operator):
    bl_idname = "vertexcolor.set"
    bl_label = "SET COLOR"
    number = bpy.props.IntProperty()

    def execute(self, context):
        tools.set_vertex_color(context, self.number)
        return{'FINISHED'}

class ButtonVertexColorCreateLayer(bpy.types.Operator):
    bl_idname = "vertexcolor.create_layer"
    bl_label = "Create Vertex Color Layer"

    def execute(self, context):
        helpers.create_color_layer(context)
        return{'FINISHED'}

class ButtonVertexColorCreateLayer(bpy.types.Operator):
    bl_idname = "alphacolor.create_layer"
    bl_label = "Create Alpha Color Layer"

    def execute(self, context):
        helpers.create_alpha_layer(context)
        return{'FINISHED'}

class ButtonBakeShadow(bpy.types.Operator):
    bl_idname = "lighttools.bakeshadow"
    bl_label = "Bake Shadow"

    def execute(self, context):
        tools.bake_shadow(self, context)
        return{'FINISHED'}

class ButtonBakeLightToVertex(bpy.types.Operator):
    bl_idname = "lighttools.bakevertex"
    bl_label = "Bake light"

    def execute(self, context):
        tools.bake_vertex(self, context)
        return{'FINISHED'}

class ButtonEnableTextureMode(bpy.types.Operator):
    bl_idname = "helpers.enable_texture_mode"
    bl_label = "Enable Texture Mode"

    def execute(self, context):
        helpers.enable_texture_mode()
        return{'FINISHED'}
