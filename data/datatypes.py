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
    "string": None,  # Special handling for variable-length strings
    "bool": "?"
}

# common attributes for binary file formats
COMMON_ATTRIBUTES = {
    "byte_order": ["little", "big"],
    

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
def pack_string(data, length_type="uint16", encoding="utf-8"):
    length_format = get_struct_format(length_type)
    encoded = data.encode(encoding)
    return struct.pack(length_format, len(encoded)) + encoded

# TODO: Reimplement after testing with strings
# Unpacking for strings with length prefix
def unpack_string(data, length_type="uint16", encoding="utf-8"):
    length_format = get_struct_format(length_type)
    length = struct.calcsize(length_format)
    length = struct.unpack(length_format, data[:length])[0]
    return data[length:].decode(encoding)