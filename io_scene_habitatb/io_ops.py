# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion
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


class ImportPRM(bpy.types.Operator, ImportHelper):
    """Import Re-Volt Mesh (.prm, .m)"""
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
    """Import Re-Volt World (.w)"""
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
    """Import Re-Volt Collision (.ncp)"""
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

class ImportPOS(bpy.types.Operator, ImportHelper):
    """Import Re-Volt POS Nodes (.pan)"""
    bl_idname = "import_scene.pan"
    bl_label = 'Import POS'
    bl_options = {'UNDO'}

    filename_ext = ".pan"
    filter_glob = StringProperty(
            default="*.pan",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))

    def execute(self, context):
        from . import import_pos

        return import_pos.load(
            self,
            self.properties.filepath,
            context,
            axis_conversion(to_up = self.up_axis,
                            to_forward = self.forward_axis).to_4x4() * self.scale)

class ImportFIN(bpy.types.Operator, ImportHelper):
    """Import Re-Volt instances (.fin)"""
    bl_idname = "import_scene.fin"
    bl_label = 'Import FIN'
    bl_options = {'UNDO'}

    filename_ext = ".fin"
    filter_glob = StringProperty(
            default="*.fin",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))

    def execute(self, context):
        from . import import_fin

        return import_fin.load(
            self,
            self.properties.filepath,
            context,
            axis_conversion(to_up = self.up_axis,
                            to_forward = self.forward_axis).to_4x4() * self.scale)


class ImportCAR(bpy.types.Operator, ImportHelper):
    """Import car from parameters.txt"""
    bl_idname = "import_scene.car"
    bl_label = 'Import Car'
    bl_options = {'UNDO'}

    filename_ext = ".txt"
    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))

    def execute(self, context):
        from . import import_car

        return import_car.load(
            self,
            self.properties.filepath,
            context,
            axis_conversion(to_up = self.up_axis,
                            to_forward = self.forward_axis).to_4x4() * self.scale)



class ExportPRM(bpy.types.Operator, ExportHelper):
    """Export object as Re-Volt Mesh (.prm, .m)"""
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
    """Export Re-Volt World (.w)"""
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
    """Export Re-Volt Collision (.ncp)"""
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

class ExportFIN(bpy.types.Operator, ExportHelper):
    """Export Re-Volt instances (.fin)"""
    bl_idname = "export_scene.prm"
    bl_label = 'Export FIN'

    filename_ext = ""
    filter_glob = StringProperty(
            default="*.fin",
            options={'HIDDEN'},
            )

    scale = FloatProperty(default=0.01, name = "Scale", min = 0.0005, max = 1, step = 0.01)
    up_axis = EnumProperty(default = "-Y", name = "Up axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))
    forward_axis = EnumProperty(default = "Z", name = "Forward axis", items = (("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")))

    def execute(self, context):
        from . import export_fin

        return export_fin.save(
            self,
            self.properties.filepath,
            context,
            axis_conversion(from_up = self.up_axis,
                            from_forward = self.forward_axis).to_4x4() * (1 / self.scale))
