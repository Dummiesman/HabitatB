# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


bl_info = {
    "name": "HabitiatB - Re-Volt File Formats",
    "author": "Dummiesman, Yethiel",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import and export Re-Volt files",
    "warning": "",
    "wiki_url": "https://github.com/Dummiesman/HabitatB/wiki",
    "support": 'COMMUNITY',
    "category": "Import-Export"}


import bpy
import bmesh
import types
import imp
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
        CollectionProperty,
        IntVectorProperty,
        PointerProperty
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )
from . import helpers, ui, parameters, const

from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion

# Completely reload the addon when hitting F8:
locals_copy = dict(locals())
for var in locals_copy:
    tmp = locals_copy[var]
    if isinstance(tmp, types.ModuleType) and tmp.__package__ == "io_scene_habitatb":
      print ("Reloading: %s"%(var))
      imp.reload(tmp)

# object properties for all rv objects
class RevoltObjectProperties(bpy.types.PropertyGroup):
    rv_type = EnumProperty(name = "Type", items = (("NONE", "None", "None"), 
                                                ("MESH", "Mesh (.prm)", "Mesh"), 
                                                ("OBJECT", "Object (.fob)", "Object"), 
                                                ("INSTANCE", "Instance (.fin)", "Instance"), 
                                                ("WORLD", "World (.w)", "World"),
                                                ("NCP", "Collision (.ncp)", "Collision (NCP)"),
                                                ("HULL", "Hull (.hul)", "Hull"),
                                                ))
    # this is for setting the object type (mesh, w, ncp, fin, ...)
    object_type = EnumProperty(name = "Object type", items = const.object_types)
    # this is the flags layer for meshes
    flags = IntVectorProperty(name = "Flags", size = 16)
    texture = IntProperty(name = "Texture") # deprecated, could be removed since textures are saved per-face now
    # this is for fin and fob file entries: each object can have unique settings. 
    # fin files have predefined settings
    flag1_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 0), set = lambda s,v: helpers.set_flag_long(s, v, 0))
    flag2_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 4), set = lambda s,v: helpers.set_flag_long(s, v, 4))
    flag3_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 8), set = lambda s,v: helpers.set_flag_long(s, v, 8))
    flag4_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 12), set = lambda s,v: helpers.set_flag_long(s, v, 12))
    # these flags can be set for objects other than the mentioned type (export .w to ncp, export prm as part of .w)
    export_as_prm = BoolProperty(name = "Additionally export as Mesh (.prm)")
    export_as_ncp = BoolProperty(name = "Additionally export as NCP (.ncp)")
    export_as_w = BoolProperty(name = "Additionally export as World (.w)")
    use_tex_num = BoolProperty(name = "Keep texture number from mesh.")

class RevoltMeshProperties(bpy.types.PropertyGroup):
    face_material = EnumProperty(name = "Material", items = const.materials, get = helpers.get_face_material, set = helpers.set_face_material)
    face_texture = IntProperty(name = "Texture", get = helpers.get_face_texture, set = helpers.set_face_texture)
    face_double_sided = BoolProperty(name = "Double sided", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_DOUBLE), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_DOUBLE))
    face_translucent = BoolProperty(name = "Translucent", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_TRANSLUCENT), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_TRANSLUCENT))
    face_mirror = BoolProperty(name = "Mirror", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_MIRROR), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_MIRROR))
    face_additive = BoolProperty(name = "Additive blending", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_TRANSL_TYPE), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_TRANSL_TYPE))
    face_texture_animation = BoolProperty(name = "Texture animation", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_TEXANIM), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_TEXANIM))
    face_no_envmapping = BoolProperty(name = "No EnvMapping (.PRM)", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_NOENV), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_NOENV))
    face_envmapping = BoolProperty(name = "EnvMapping (.W)", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_ENV), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_ENV))
    face_cloth = BoolProperty(name = "Cloth effect (.prm)", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_CLOTH), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_CLOTH))
    face_skip = BoolProperty(name = "Do not export", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_SKIP), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_SKIP))
    

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

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))


    def execute(self, context):
        from . import import_prm

        return import_prm.load(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(to_up = self.up_axis, 
                            to_forward = self.forward_axis).to_4x4() * self.scale)

class ImportW(bpy.types.Operator, ImportHelper):
    """Import from W file format (.w)"""
    bl_idname = "import_scene.w"
    bl_label = 'Import W'
    bl_options = {'UNDO'}

    filename_ext = ".w"
    filter_glob = StringProperty(
            default="*.w", 
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))

    def execute(self, context):
        from . import import_w

        return import_w.load(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(to_up = self.up_axis, 
                            to_forward = self.forward_axis).to_4x4() * self.scale)

class ImportNCP(bpy.types.Operator, ImportHelper):
    """Import from NCP file format (.ncp)"""
    bl_idname = "import_scene.ncp"
    bl_label = 'Import NCP'
    bl_options = {'UNDO'}

    filename_ext = ".ncp"
    filter_glob = StringProperty(
            default="*.ncp", 
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    
    def execute(self, context):
        from . import import_ncp

        return import_ncp.load(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(to_up = self.up_axis, 
                            to_forward = self.forward_axis).to_4x4() * self.scale)


class ExportPRM(bpy.types.Operator, ExportHelper):
    """Export to PRM file format (.prm, .m)"""
    bl_idname = "export_scene.prm"
    bl_label = 'Export PRM'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.prm;*.m",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
        
    def execute(self, context):
        from . import export_prm
                           
        return export_prm.save(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(from_up = self.up_axis, 
                            from_forward = self.forward_axis).to_4x4() * (1 / self.scale))

class ExportW(bpy.types.Operator, ExportHelper):
    """Export to W file format (.w)"""
    bl_idname = "export_scene.w"
    bl_label = 'Export W'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.w",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
        
    def execute(self, context):
        from . import export_w
                           
        return export_w.save(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(from_up = self.up_axis, 
                            from_forward = self.forward_axis).to_4x4() * (1 / self.scale))


class ExportNCP(bpy.types.Operator, ExportHelper):
    """Export to PRM file format (.prm, .m)"""
    bl_idname = "export_scene.ncp"
    bl_label = 'Export NCP'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.ncp;*.m",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
        
    def execute(self, context):
        from . import export_ncp
        
                                    
        return export_ncp.save(
            self, 
            self.properties.filepath, 
            context, 
            axis_conversion(from_up = self.up_axis, from_forward = self.forward_axis).to_4x4() * (1 / self.scale))


# add menu entries
# PRM
def menu_func_export_prm(self, context):
    self.layout.operator(ExportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")

def menu_func_import_prm(self, context):
    self.layout.operator(ImportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")

# NCP
def menu_func_import_ncp(self, context):
    self.layout.operator(ImportNCP.bl_idname, text="Re-Volt NCP (.ncp)")

def menu_func_export_ncp(self, context):
    self.layout.operator(ExportNCP.bl_idname, text="Re-Volt NCP (.ncp)")

# W
def menu_func_import_w(self, context):
    self.layout.operator(ImportW.bl_idname, text="Re-Volt World (.w)")

def menu_func_export_w(self, context):
    self.layout.operator(ExportW.bl_idname, text="Re-Volt World (.w)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import_prm)
    bpy.types.INFO_MT_file_import.append(menu_func_import_ncp)
    bpy.types.INFO_MT_file_import.append(menu_func_import_w)
    bpy.types.INFO_MT_file_export.append(menu_func_export_prm)
    bpy.types.INFO_MT_file_export.append(menu_func_export_ncp)
    bpy.types.INFO_MT_file_export.append(menu_func_export_w)

    #bpy.types.Scene.ui_properties = bpy.props.PointerProperty(type=ui.UIProperties)

    bpy.types.Object.revolt = PointerProperty(type = RevoltObjectProperties)
    bpy.types.Mesh.revolt = PointerProperty(type = RevoltMeshProperties)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import_prm)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_ncp)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_w)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_ncp)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_w)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_prm)

    # del bpy.types.Scene.ui_properties

    del bpy.types.Object.revolt
    del bpy.types.Mesh.revolt


if __name__ == "__main__":
    register()
