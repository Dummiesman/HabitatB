import mathutils

def vc_to_bitfield(color_layer):
    flags_b0 = int(color_layer[0] * 255.0)
    flags_b1 = int(color_layer[2] * 255.0)
    flags_ba = bytearray([flags_b0, flags_b1])
    flags_int = int.from_bytes(flags_ba, byteorder='little', signed=False)
    return flags_int

def bitfield_to_vc(number):
    flags_bytes = number.to_bytes(2, byteorder='little', signed=False)
    flagR = float(flags_bytes[0]) / 255.0
    flagB = float(flags_bytes[1]) / 255.0
    return mathutils.Color((flagR, 1.0, flagB))

