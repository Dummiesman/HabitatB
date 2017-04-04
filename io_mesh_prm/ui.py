# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####

import bpy
import bmesh
from . import helpers

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


"""
keeping this for future reference
flag_names = ["Invisible", "Mirroring", 
        "No EnvMap", "Double-Sided", 
        "Additive Blending", "EnvMap", 
        "Translucent", "Texture Animation", 
        "Cloth Effect"
        ]
"""


flags = [0x002, 0x004, 0x100, 0x400, 0x800]

# type constants and names
RV_CAR, RV_OBJECT, RV_INSTANCE, RV_WORLD = range(4)
type_names = ["Car", "Game Object", "Mesh Instance", "World Mesh"]
type_icons = ["AUTO", "EMPTY_DATA", "OBJECT_DATA", "WORLD"]

enum_types = (('0', 'Car', ''), ('1', 'Game Object', ''), ('2', 'Mesh Instance', ''), ('3', 'World Mesh', ''))

prop_states = [0, 0, 0, 0, 0, 0]

class UIProperties(bpy.types.PropertyGroup):
    rv_type = bpy.props.EnumProperty(
        items = enum_types, update = lambda self, context: set_rv_type(self, context, 'rv_type')
    )



# type selection buttons for use in various panels
def type_selection(row, context):
    row.alignment = 'EXPAND'
    # row.prop(context.object, 'rv_type', expand=True)
    row.operator("obproperties.set", text="Car", icon=type_icons[RV_CAR]).number=RV_CAR
    row.operator("obproperties.set", text="Object", icon=type_icons[RV_OBJECT]).number=RV_OBJECT
    row.operator("obproperties.set", text="Instance", icon=type_icons[RV_INSTANCE]).number=RV_INSTANCE
    row.operator("obproperties.set", text="World", icon=type_icons[RV_WORLD]).number=RV_WORLD

# main panel for selecting the object type
class RevoltTypePanel(bpy.types.Panel):
    bl_label = "Re-Volt Object Type"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        obj = context.object
        scene = context.scene
        row = self.layout.row()

        # check if the object has an rv type
        if "rv_type" in obj: 
            row.label(text="Type: {}".format(type_names[obj["rv_type"]]), icon=type_icons[obj["rv_type"]])
        else:
            row.label(text="Please set the type of this object.", icon='INFO')

        # Type selection
        row = self.layout.row(align=True)
        # row.prop(scene.ui_properties, "rv_type", text = "Type", expand=True)
        type_selection(row, context)

# panel for setting per-polygon mesh properties
class RevoltPropertiesPanel(bpy.types.Panel):
    bl_label = "Re-Volt Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    selected_face_count = None
    selection = None
    
    # @classmethod
    # def poll(cls, context):
    #     # Only allow in edit mode for a selected mesh.
    #     # it might be better to show this panel all the time and just show a warning when not in edit mode
    #     return context.mode == "EDIT_MESH" and context.object is not None and context.object.type == "MESH"
 
    def draw(self, context):
        obj = context.object
        row = self.layout.row(align=True)

        # check if the object has an rv type
        if not "rv_type" in obj:
            row = self.layout.row(align=True)
            row.label(text="Please set the type of this object.", icon='INFO')

            # Type selection
            row = self.layout.row(align=True)

        if context.mode != "EDIT_MESH":
            row = self.layout.row()
            row.label(text="Please enable Edit Mode to set properties.", icon='INFO')

        elif "rv_type" in obj: # EDIT MODE
            # draw stuff
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            flag_layer = bm.loops.layers.color.get("flags")
           
            # update selection data
            if self.selected_face_count is None or self.selected_face_count != mesh.total_face_sel:
                self.selected_face_count = mesh.total_face_sel
                self.selection = [face for face in bm.faces if face.select]
        
            if flag_layer is None:
                row = self.layout.row()
                row.label(text="Please create a properties (flags) layer.", icon='INFO')
                row = self.layout.row()
                row.operator("properties.create_layer", icon='PLUS')

            elif self.selection:
                # number of selected faces
                self.layout.row().label(text="{} faces selected.".format(self.selected_face_count))
                row = self.layout.row()
                row.label(text="Toggle Property")
                row.label(text="Status")
                # list of properties and buttons, create a button for each
                for prop in range(len(flag_names)):

                    # filter unapplicable flags
                    if not ((obj["rv_type"] in [RV_CAR, RV_INSTANCE, RV_OBJECT] and prop == 4) or (obj["rv_type"] == RV_WORLD and prop == 3)):

                        # create a new row
                        row = self.layout.row()
                        # place a button
                        row.operator("properties.set_prop", icon='NONE', text=flag_names[prop]).number=prop
                        # place a status label
                        num_set = 0
                        for face in self.selection:
                            bf = helpers.vc_to_bitfield(face.loops[0][flag_layer])
                            if bf & flags[prop]: # check if the flag is checked
                                num_set += 1
                        if num_set == 0: # none are set
                            ico = "X"
                            txt = "Not set"
                            prop_states[prop] = 1 # enable all on button press
                        elif num_set == self.selected_face_count: # all are set
                            ico = "FILE_TICK"
                            txt = "Set"
                            prop_states[prop] = 0 # disable all on button press
                        else: # some are set
                            ico = "DOTSDOWN"
                            txt = "Set for {} of {}".format(num_set, self.selected_face_count)
                            prop_states[prop] = 1 # enable all on button press

                        row.label(text=txt, icon=ico)

            else:
                self.layout.row().label(text="Select at least one face.", icon='INFO')

# panel for setting vertex colors
class RevoltVertexPanel(bpy.types.Panel):
    bl_label = "HabitatB Vertex Colors (not implemented)"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

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
                row.operator("vertexcolor.set", text="Not implemented.")
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


class ButtonPropertiesCreateLayer(bpy.types.Operator):
    bl_idname = "properties.create_layer"
    bl_label = "Create properties (flags) layer"
    number = bpy.props.IntProperty()
 
    def execute(self, context):
        create_flags_layer(context)
        return{'FINISHED'}    

class ButtonPropertiesSetProp(bpy.types.Operator):
    bl_idname = "obproperties.set"
    bl_label = "Set as type"
    number = bpy.props.IntProperty()
 
    def execute(self, context):
        set_rv_type(context, self.number)
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

class ButtonPropertiesSet(bpy.types.Operator):
    bl_idname = "properties.set_prop"
    bl_label = "Property"
    bl_description = "Toggle this property"
    number = bpy.props.IntProperty()

    def draw(self, context):
        self.bl_description = flag_descr[self.number]
 
    def execute(self, context):
        set_flag(context, flags[self.number], prop_states[self.number])
        return{'FINISHED'}    

def set_vertex_color(context, number):
    print(context, number)

def set_rv_type(context, type):
    obj = context.object
    obj['rv_type'] = type

def create_flags_layer(context):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.loops.layers.color.new("flags")

def create_color_layer(context):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.loops.layers.color.new("color")

def set_flag(context, flag, status=-1):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    flag_layer = bm.loops.layers.color.get("flags")
    print("DEBUG: Toggle flag {}".format(str(flag)))
    for face in bm.faces:
        if face.select:
            for loop in face.loops:
                vc = loop[flag_layer]
                bf = helpers.vc_to_bitfield(vc)
                if status == 1: # enable flag
                    bf |= flag
                elif status == 0: # disable flag
                    bf = bf & (~flag)
                else: # toggle
                    if not bf & flag:
                        bf |= flag
                    else:
                        bf = bf & (~flag)

                loop[flag_layer] = helpers.bitfield_to_vc(bf)