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
from . import helpers, ui, parameters

from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion

# Completely reload the addon when hitting F8:
locals_copy = dict(locals())
for var in locals_copy:
    tmp = locals_copy[var]
    if isinstance(tmp, types.ModuleType) and tmp.__package__ == "io_scene_habitatb":
      print ("Reloading: %s"%(var))
      imp.reload(tmp)

object_types = [
    ("OBJECT_TYPE_CAR", "Car", "Car", "", -1),
    ("OBJECT_TYPE_BARREL", "Barrel", "Barrel", "", 1),
    ("OBJECT_TYPE_BEACHBALL", "Beachball", "Beachball", "", 2),
    ("OBJECT_TYPE_PLANET", "Planet", "Planet", "", 3),
    ("OBJECT_TYPE_PLANE", "Plane", "Plane", "", 4),
    ("OBJECT_TYPE_COPTER", "Copter", "Copter", "", 5),
    ("OBJECT_TYPE_DRAGON", "Dragon", "Dragon", "", 6),
    ("OBJECT_TYPE_WATER", "Water", "Water", "", 7),
    ("OBJECT_TYPE_TROLLEY", "Trolley", "Trolley", "", 8),
    ("OBJECT_TYPE_BOAT", "Boat", "Boat", "", 9),
    ("OBJECT_TYPE_SPEEDUP", "Speedup", "Speedup", "", 10),
    ("OBJECT_TYPE_RADAR", "Radar", "Radar", "", 11),
    ("OBJECT_TYPE_BALLOON", "Balloon", "Balloon", "", 12),
    ("OBJECT_TYPE_HORSE", "Horse", "Horse", "", 13),
    ("OBJECT_TYPE_TRAIN", "Train", "Train", "", 14),
    ("OBJECT_TYPE_STROBE", "Strobe", "Strobe", "", 15),
    ("OBJECT_TYPE_FOOTBALL", "Football", "Football", "", 16),
    ("OBJECT_TYPE_SPARKGEN", "Sparkgen", "Sparkgen", "", 17),
    ("OBJECT_TYPE_SPACEMAN", "Spaceman", "Spaceman", "", 18),
    ("OBJECT_TYPE_SHOCKWAVE", "Shockwave", "Shockwave", "", 19),
    ("OBJECT_TYPE_FIREWORK", "Firework", "Firework", "", 20),
    ("OBJECT_TYPE_PUTTYBOMB", "Puttybomb", "Puttybomb", "", 21),
    ("OBJECT_TYPE_WATERBOMB", "Waterbomb", "Waterbomb", "", 22),
    ("OBJECT_TYPE_ELECTROPULSE", "Electropulse", "Electropulse", "", 23),
    ("OBJECT_TYPE_OILSLICK", "Oilslick", "Oilslick", "", 24),
    ("OBJECT_TYPE_OILSLICK_DROPPER", "Oilslick dropper", "Oilslick dropper", "", 25),
    ("OBJECT_TYPE_CHROMEBALL", "Chromeball", "Chromeball", "", 26),
    ("OBJECT_TYPE_CLONE", "Clone", "Clone", "", 27),
    ("OBJECT_TYPE_TURBO", "Turbo", "Turbo", "", 28),
    ("OBJECT_TYPE_ELECTROZAPPED", "Electrozapped", "Electrozapped", "", 29),
    ("OBJECT_TYPE_SPRING", "Spring", "Spring", "", 30),
    ("OBJECT_TYPE_PICKUP", "Pickup", "Pickup", "", 31),
    ("OBJECT_TYPE_DISSOLVEMODEL", "Dissolve model", "Dissolve model", "", 32),
    ("OBJECT_TYPE_FLAP", "Flap", "Flap", "", 33),
    ("OBJECT_TYPE_LASER", "Laser", "Laser", "", 34),
    ("OBJECT_TYPE_SPLASH", "Splash", "Splash", "", 35),
    ("OBJECT_TYPE_BOMBGLOW", "Bombglow", "Bombglow", "", 36),
    ("OBJECT_TYPE_MAX", "Max", "Max", "", 37),
    ]

# Object types and properties
# The flags are for the .fob file and the .fin file (game objects and mesh instances)
class RevoltObjectProperties(bpy.types.PropertyGroup):
    rv_type = EnumProperty(name = "Type", items = (("NONE", "None", "None"), 
                                                ("MESH", "Mesh (.prm)", "Mesh"), 
                                                ("OBJECT", "Object (.fob)", "Object"), 
                                                ("INSTANCE", "Instance (.fin)", "Instance"), 
                                                ("WORLD", "World (.w)", "World"),
                                                ("NCP", "Collision (.ncp)", "Collision (NCP)"),
                                                ("HULL", "Hull (.hul)", "Hull"),
                                                ))
    object_type = EnumProperty(name = "Object type", items = object_types)
    flags = IntVectorProperty(name = "Flags", size = 16)
    flag1_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 0), set = lambda s,v: helpers.set_flag_long(s, v, 0))
    flag2_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 4), set = lambda s,v: helpers.set_flag_long(s, v, 4))
    flag3_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 8), set = lambda s,v: helpers.set_flag_long(s, v, 8))
    flag4_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 12), set = lambda s,v: helpers.set_flag_long(s, v, 12))
    texture = IntProperty(name = "Texture")

class RevoltMeshProperties(bpy.types.PropertyGroup):
    face_material = EnumProperty(name = "Material", items = helpers.materials, get = helpers.get_face_material, set = helpers.set_face_material)
    face_texture = IntProperty(name = "Texture", get = helpers.get_face_texture, set = helpers.set_face_texture)
    face_double_sided = BoolProperty(name = "Double sided", get = lambda s: bool(helpers.get_face_property(s) & 2), set = lambda s,v: helpers.set_face_property(s, v, 2))
    face_translucent = BoolProperty(name = "Translucent", get = lambda s: bool(helpers.get_face_property(s) & 4), set = lambda s,v: helpers.set_face_property(s, v, 4))
    face_mirror = BoolProperty(name = "Mirror", get = lambda s: bool(helpers.get_face_property(s) & 128), set = lambda s,v: helpers.set_face_property(s, v, 128))
    face_additive = BoolProperty(name = "Additive blending", get = lambda s: bool(helpers.get_face_property(s) & 256), set = lambda s,v: helpers.set_face_property(s, v, 256))
    face_texture_animation = BoolProperty(name = "Texture animation", get = lambda s: bool(helpers.get_face_property(s) & 512), set = lambda s,v: helpers.set_face_property(s, v, 512))
    face_no_envmapping = BoolProperty(name = "No EnvMapping (.PRM)", get = lambda s: bool(helpers.get_face_property(s) & 1024), set = lambda s,v: helpers.set_face_property(s, v, 1024))
    face_envmapping = BoolProperty(name = "EnvMapping (.W)", get = lambda s: bool(helpers.get_face_property(s) & 2048), set = lambda s,v: helpers.set_face_property(s, v, 2048))
    export_as_prm = BoolProperty(name = "Export as mesh (.PRM)")
    export_as_ncp = BoolProperty(name = "Export as hitbox (.NCP)")
    export_as_w = BoolProperty(name = "Export as world (.W)")

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
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "up_axis",
                                            "scale",
                                            "forward_axis",
                                            "filter_glob",
                                            "check_existing",

                                            ))

        return import_ncp.load(self, context, axis_conversion(to_up = self.up_axis, to_forward = self.forward_axis).to_4x4() * self.scale, self.properties.filepath)


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
        
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
                                    
        return export_ncp.save(self, context, axis_conversion(from_up = self.up_axis, from_forward = self.forward_axis).to_4x4() * (1 / self.scale), self.properties.filepath)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")

def menu_func_import(self, context):
    self.layout.operator(ImportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")


def menu_func_import_ncp(self, context):
    self.layout.operator(ImportNCP.bl_idname, text="Re-Volt NCP (.ncp)")

def menu_func_export_ncp(self, context):
    self.layout.operator(ExportNCP.bl_idname, text="Re-Volt NCP (.ncp)")



def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_import.append(menu_func_import_ncp)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_export.append(menu_func_export_ncp)

    #bpy.types.Scene.ui_properties = bpy.props.PointerProperty(type=ui.UIProperties)

    bpy.types.Object.revolt = PointerProperty(type = RevoltObjectProperties)
    bpy.types.Mesh.revolt = PointerProperty(type = RevoltMeshProperties)



def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_ncp)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_ncp)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    # del bpy.types.Scene.ui_properties

    del bpy.types.Object.revolt
    del bpy.types.Mesh.revolt



if __name__ == "__main__":
    register()
