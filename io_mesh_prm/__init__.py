# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####


bl_info = {
    "name": "HabitiatB - Re-Volt PRM",
    "author": "Dummiesman, Yethiel",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import and export Re-Volt PRM files",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.7/Py/"
                "Scripts/Import-Export/DummiesmanPRM",
    "support": 'COMMUNITY',
    "category": "Import-Export"}


import bpy
import bmesh
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )
from . import helpers

prop_states = [0, 0, 0, 0, 0, 0]

"""
flag_names = ["Invisible", "Mirroring", 
        "No EnvMap", "Double-Sided", 
        "Additive Blending", "EnvMap", 
        "Translucent", "Texture Animation", 
        "Cloth Effect"
        ]
"""
flag_names = ["Double-Sided", "Transparent", "Alpha or Additive", "No EnvMap", "EnvMap"]
flag_descr = ["Set to make the polygon visible from both sides.", 
            "Set to enable transparency for this polygon. Re-Volt will then apply transparency from the texture and the alpha vertex color channel.", 
            "Set to make Re-Volt render this polygon with alpha transparency from the texture or use additive blending (dark colors become transparent, brighter colors lighten/glow).",
            "Set to disable the environment map (don't make the polygon shiny, e.g. for the underside of cars)." 
            "Set to enable the environment map (make the polygon shiny)."]

flags = [0x002, 0x004, 0x100, 0x400, 0x800]

RV_CAR, RV_OBJECT, RV_INSTANCE, RV_WORLD = range(4)
type_names = ["Car", "Game Object", "Mesh Instance", "World Mesh"]

class ImportPRM(bpy.types.Operator, ImportHelper):
    """Import from PRM file format (.prm, .m)"""
    bl_idname = "import_scene.prm"
    bl_label = 'Import PRM'
    bl_options = {'UNDO'}

    filename_ext = ".prm"
    filter_glob = StringProperty(
            default="*.prm;*.m", 
            options={'HIDDEN'},
            )

    def execute(self, context):
        from . import import_prm
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        return import_prm.load(self, context, **keywords)


class ExportPRM(bpy.types.Operator, ExportHelper):
    """Export to PRM file format (.prm, .m)"""
    bl_idname = "export_scene.prm"
    bl_label = 'Export PRM'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.prm;*.m",
            options={'HIDDEN'},
            )
        
    def execute(self, context):
        from . import export_prm
        
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
                                    
        return export_prm.save(self, context, **keywords)

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

        if "rv_type" in obj: row.label(text="Type: {}".format(type_names[obj["rv_type"]]))

        # check if the object has an rv type
        if not "rv_type" in obj:
            row = self.layout.row(align=True)
            row.label(text="Please set the type of this object.", icon='INFO')

        # Type selection
        row = self.layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("obproperties.set", text="Car", icon='AUTO').number=RV_CAR
        row.operator("obproperties.set", text="Object", icon='EMPTY_DATA').number=RV_OBJECT
        row.operator("obproperties.set", text="Instance", icon='OBJECT_DATA').number=RV_INSTANCE
        row.operator("obproperties.set", text="World", icon='WORLD').number=RV_WOLRD
    

        if context.mode != "EDIT_MESH":
            row = self.layout.row()
            row.label(text="Please enable Edit Mode to set properties.", icon='INFO')

        if "rv_type" in obj: # EDIT MODE
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


           
class ButtonPropertiesCreateLayer(bpy.types.Operator):
    bl_idname = "properties.create_layer"
    bl_label = "Create properties (flags) layer"
    number = bpy.props.IntProperty()
 
    def execute(self, context):
        create_flags_layer(context)
        return{'FINISHED'}    

class ButtonPropertiesCreateLayer(bpy.types.Operator):
    bl_idname = "obproperties.set"
    bl_label = "Set as type"
    number = bpy.props.IntProperty()
 
    def execute(self, context):
        set_rv_type(context, self.number)
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

def set_rv_type(context, typenum):
    obj = context.object
    obj['rv_type'] = typenum

def create_flags_layer(context):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.loops.layers.color.new("flags")

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

# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")


def menu_func_import(self, context):
    self.layout.operator(ImportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
