import struct

# List of numeric data types
NUMERIC_TYPES = {
    "int": ["int8", "int16", "int32", "int64"],
    "uint": ["uint8", "uint16", "uint32", "uint64"],
    "float": ["float", "double"]
}

# List of string-related data types
STRING_TYPES = ["char", "string"]

# List of boolean types
BOOLEAN_TYPES = ["bool"]

# Helper: Flattened list of all supported data types
ALL_DATA_TYPES = (
    NUMERIC_TYPES["int"]
    + NUMERIC_TYPES["uint"]
    + NUMERIC_TYPES["float"]
    + STRING_TYPES
    + BOOLEAN_TYPES
)

# Map of data types to struct format strings
STRUCT_FORMAT_MAP = {
    "int8": "b",
    "int16": "h",
    "int32": "i",
    "int64": "q",
    "uint8": "B",
    "uint16": "H",
    "uint32": "I",
    "uint64": "Q",
    "float": "f",
    "double": "d",
    "char": "c",  # Single character
    "string": "Bs",  # Always includes the string length as an uint8 as prefix
    "bool": "?"
}

# common attributes for binary file formats
COMMON_ATTRIBUTES = {
    # Byte order options
    "byte_order": ["little", "big"],

    # Vertex attributes (position, normals, etc.)
    "vertex": {
        "position": ["float32", "float64"],  # Common data types for position
        "normal": ["float32", "float64"],    # Normal vectors
        "texcoord": ["float32", "float64"],  # Texture coordinates (UVs)
    },

    # Color attributes
    "color": {
        "rgba": ["uint8"],  # 8-bit per channel color
        "rgb": ["uint8"],   # 8-bit per channel without alpha
        "float": ["float32"],  # Floating-point colors
    },

    # Face data attributes
    "face": {
        "indices": ["int32", "uint32"],  # Vertex indices for faces
        "material_id": ["int16", "uint16"],  # Material IDs
        "normal": ["int32", "uint32"],   # Face normals
        "uv": ["int32", "uint32"],       # UV coordinates
    },

    # Additional attributes
    "metadata": {
        "name": ["string"],  # Name of the object
        "id": ["uint32"],    # Object ID
        "timestamp": ["uint64"],  # Time-related metadata
    },
    
    # Animation attributes (if relevant for 3D files)
    "animation": {
        "joint_indices": ["int16", "uint16"],  # Bone indices
        "weights": ["float32"],               # Skinning weights
    },
}

COMMON_ATTRIBUTES2 = {
    # Byte order options
    "byte_order": ["little", "big"],
    # Vertex attributes (position, normals, etc.)
    "vertex": ["float32", "float64"],  # Common data types for position
    "normal": ["float32", "float64"],    # Normal vectors
    "texcoord": ["float32", "float64"],  # Texture coordinates (UVs)
    # Color attributes
    "color": ["uint8"],  # 8-bit per channel color
    # face data attributes
    # can be sequential or separate (e.g. seperate: all faces then all face normals etc., sequential: face1, normal1, uv1, face2, normal2, uv2 etc.)
    "face": ["int32", "uint32"],  # Vertex indices for faces
    "material_id": ["int16", "uint16"],  # Material IDs (not suporrted right now)
    "face_normal": ["int32", "uint32"],   # Face normals
    "face_texcoord": ["int32", "uint32"],   # UV coordinates
    # Additional attributes

    # Animation attributes (if relevant for 3D files)
}


# Checks if a given data type is valid.
# :param data_type: The data type to check (string).
# :return: True if valid, False otherwise.
def is_valid_type(data_type): 
    return data_type in STRUCT_FORMAT_MAP and STRUCT_FORMAT_MAP[data_type] is not None


# Gets the struct format string for a given data type.
# :param data_type: The data type to look up.
# :return: The struct format string or raises an error if invalid.
def get_struct_format(data_type):
    if is_valid_type(data_type):
        return STRUCT_FORMAT_MAP[data_type]
    raise ValueError(f"Invalid data type: {data_type}")

# Packing for strings with length prefix
# :param data: The string to pack.
# :param length_format: The format string for the length prefix.
# :param encoding: The encoding to use for the string. (endianess is based on the encoding)
def pack_string(data, length_format="B", encoding="utf-8"):
    encoded = data.encode(encoding)
    return struct.pack(length_format, len(encoded)) + encoded


# Unpacking for strings with length prefix
# :param data: The binary data to unpack.
# :param length_format: The format string for the length prefix.
# :param encoding: The encoding to use for the string. (endianess is based on the encoding)
def unpack_string(data, length_format="B", encoding="utf-8"):
    prefix_length = struct.calcsize(length_format)
    string_length = struct.unpack(length_format, data.read(prefix_length))[0]
    return data.read(string_length).decode(encoding)