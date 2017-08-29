# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


bl_info = {
    "name": "HabitatB - Re-Volt File Formats",
    "author": "Dummiesman, Yethiel",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import and export Re-Volt files",
    "warning": "",
    "wiki_url": "http://learn.re-volt.io/habitatb-docs",
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
        FloatVectorProperty,
        PointerProperty
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )
from . import io_ops, helpers, panels, parameters, const

from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion

from bpy.app.handlers import persistent


# Completely reload the addon when hitting F8:
locals_copy = dict(locals())
for var in locals_copy:
    tmp = locals_copy[var]
    if isinstance(tmp, types.ModuleType) and tmp.__package__ == "io_scene_habitatb":
      print ("Reloading: %s"%(var))
      imp.reload(tmp)

# object properties for all rv objects
class RevoltObjectProperties(bpy.types.PropertyGroup):
    # this is for setting the object type (mesh, w, ncp, fin, ...)
    rv_type = EnumProperty(name = "Type", items = (("NONE", "None", "None"),
                                                ("MESH", "Mesh (.prm)", "Mesh"),
                                                #("OBJECT", "Object (.fob)", "Object"),
                                                ("INSTANCE", "Instance (.fin)", "Instance"),
                                                ("WORLD", "World (.w)", "World"),
                                                ("NCP", "Collision (.ncp)", "Collision (NCP)"),
                                                #("HULL", "Hull (.hul)", "Hull"),
                                                ))
    object_type = EnumProperty(name = "Object type", items = const.object_types)
    # this is the flags layer for meshes
    flags = IntVectorProperty(name = "Flags", size = 16)
    texture = IntProperty(name = "Texture") # deprecated, could be removed since textures are saved per-face now

    # instances
    fin_col = FloatVectorProperty(
                                   name="Model color",
                                   subtype='COLOR',
                                   default=(1.0, 1.0, 1.0),
                                   min=0.0, max=1.0,
                                   description=""
                                   )
    fin_envcol = FloatVectorProperty(
                                   name="Env Color",
                                   subtype='COLOR',
                                   default=(1.0, 1.0, 1.0, 1.0),
                                   min=0.0, max=1.0,
                                   description="Color of the EnvMap",
                                   size=4
                                   )
    fin_priority = IntProperty(name="Priority", default=1)
    fin_flag_env = BoolProperty(name="Use Environment Map", default=True)
    fin_flag_model_rgb = BoolProperty(name="Use Model Color", default=False)
    fin_flag_hide = BoolProperty(name="Hide", default=False)
    fin_flag_no_mirror = BoolProperty(name="Don't show in Mirror Mode", default=False)
    fin_flag_no_lights = BoolProperty(name="Is affected by Light", default=False)
    fin_flag_no_camera_coll = BoolProperty(name="No Camera Collision", default=False)
    fin_flag_no_object_coll = BoolProperty(name="No Object Collision", default=False)
    fin_lod_bias = IntProperty(name="LoD Bias", default = 1024)

    # these flags can be set for objects other than the mentioned type (export .w to ncp, export prm as part of .w)
    export_as_ncp = BoolProperty(name = "Additionally export as NCP (.ncp)")
    export_as_w = BoolProperty(name = "Additionally export as World (.w)")
    use_tex_num = BoolProperty(name = "Keep texture number from mesh.")
    light1 = EnumProperty(name = "Light 1", items = const.lights, default = "SUN")
    light2 = EnumProperty(name = "Light 2", items = const.lights, default = "HEMI")
    light_intensity1 = FloatProperty(name = "Intensity 1", min=0.0, default=1)
    light_intensity2 = FloatProperty(name = "Intensity 2", min=0.0, default=.1)
    light_orientation = EnumProperty(name = "Orientation", items=const.light_orientations, default = "Z")
    shadow_method = EnumProperty(name = "Method", items=const.shadow_methods)
    shadow_quality = IntProperty(name = "Quality", min=0, max=32, default=8)
    shadow_resolution = IntProperty(name = "Resolution", min=32, max=8192, default=128)
    shadow_softness = FloatProperty(name = "Softness", min=0.0, max=100.0, default=0.5)
    shadow_table = StringProperty(name = "Shadowtable", default="")
    vertex_color_picker = FloatVectorProperty(
                                   name="object_color",
                                   subtype='COLOR',
                                   default=(1.0, 1.0, 1.0),
                                   min=0.0, max=1.0,
                                   description="color picker"
                                   )


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

# class RevoltUIProperties(bpy.types.PropertyGroup):

# add menu entries
# PRM
def menu_func_export_prm(self, context):
    self.layout.operator(io_ops.ExportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")

def menu_func_import_prm(self, context):
    self.layout.operator(io_ops.ImportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")

# NCP
def menu_func_import_ncp(self, context):
    self.layout.operator(io_ops.ImportNCP.bl_idname, text="Re-Volt NCP (.ncp)")

def menu_func_export_ncp(self, context):
    self.layout.operator(io_ops.ExportNCP.bl_idname, text="Re-Volt NCP (.ncp)")

# W
def menu_func_import_w(self, context):
    self.layout.operator(io_ops.ImportW.bl_idname, text="Re-Volt World (.w)")

def menu_func_export_w(self, context):
    self.layout.operator(io_ops.ExportW.bl_idname, text="Re-Volt World (.w)")

# POS
def menu_func_import_pos(self, context):
    self.layout.operator(io_ops.ImportPOS.bl_idname, text="Re-Volt Position Nodes (.pan)")

# FIN
def menu_func_import_fin(self, context):
    self.layout.operator(io_ops.ImportFIN.bl_idname, text="Re-Volt Instances (.fin)")

def menu_func_export_fin(self, context):
    self.layout.operator(io_ops.ExportFIN.bl_idname, text="Re-Volt Instances (.fin)")

# CAR
def menu_func_import_car(self, context):
    self.layout.operator(io_ops.ImportCAR.bl_idname, text="Re-Volt Car (parameters.txt)")
global_dict = {}

@persistent
def edit_object_change_handler(scene):
    """ For accessing and chaning custom layers from the panels """
    obj = scene.objects.active
    if obj is None:
        return None

    if obj.mode == 'EDIT' and obj.type == 'MESH':
        global_dict.setdefault(obj.name, bmesh.from_edit_mesh(obj.data))
        return None

    global_dict.clear()
    return None

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import_prm)
    bpy.types.INFO_MT_file_import.append(menu_func_import_ncp)
    bpy.types.INFO_MT_file_import.append(menu_func_import_w)
    bpy.types.INFO_MT_file_import.append(menu_func_import_pos)
    bpy.types.INFO_MT_file_import.append(menu_func_import_fin)
    bpy.types.INFO_MT_file_import.append(menu_func_import_car)

    bpy.types.INFO_MT_file_export.append(menu_func_export_prm)
    bpy.types.INFO_MT_file_export.append(menu_func_export_ncp)
    bpy.types.INFO_MT_file_export.append(menu_func_export_w)
    bpy.types.INFO_MT_file_export.append(menu_func_export_fin)


    bpy.types.Object.revolt = PointerProperty(type = RevoltObjectProperties)
    bpy.types.Mesh.revolt = PointerProperty(type = RevoltMeshProperties)

    bpy.app.handlers.scene_update_post.append(edit_object_change_handler)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import_prm)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_ncp)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_w)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_pos)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_fin)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_car)

    bpy.types.INFO_MT_file_export.remove(menu_func_export_ncp)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_w)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_prm)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_fin)


    del bpy.types.Object.revolt
    del bpy.types.Mesh.revolt


if __name__ == "__main__":
    register()
