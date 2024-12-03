import struct
from data.datatypes import *

# Represents a single attribute in a file format (e.g. position, normal, texcoord)
class Attribute:
    # :param name: Name of the attribute (e.g. "position", "normal", "texcoord")
    # :param data_type: Data type of the attribute (e.g. "float", "uint8")
    # :param size: Number of components in the attribute (e.g. 3 for a 3D vector)
    def __init__(self, name, data_type, size=1):
        if not is_valid_type(data_type):
            raise ValueError(f"Invalid data type: {data_type}")
        self.name = name
        self.type = data_type
        self.size = size

    # Returns the struct format string for the attribute
    def get_format_string(self):
        return get_struct_format(self.type) * self.size



# Represents a single block in a file format (e.g. "header", "vertex data", "face data")
class Block:
    # :param name: Name of the block (e.g. "header", "vertex data", "face data")
    # :param attributes: List of attributes in the block
    # :param block_terminator: Optional block terminator attribute
    def __init__(self, name, attributes = [], block_terminator = None):
        self.name = name
        self.attributes = attributes
        self.block_terminator = block_terminator

    # returns the format string for the block
    def get_format_string(self):
        return ''.join(attr.get_format_string() for attr in self.attributes)



# Represents a file format specification
class FormatSpec:

    # :param name: Name of the file format
    # :param blocks: List of blocks in the file format
    # :param endian: Endianness of the file format (default is "little")
    def __init__(self, name, blocks = [], endian = "little"):
        self.name = name
        self.blocks = blocks
        # check if endian is valid
        if endian in ["little", "big"]:
            self.endian = endian
        else:
            self.endian = "little"
            raise ValueError(f"Invalid endianness: {endian}")
        

    # Adds a block to the file format
    # :param block: Block to add
    def add_block(self, block):
        self.blocks.append(block)

    # Converts a .obj file to a binary file using the format specification
    # :param obj_file: Path to the .obj file
    def create_binary_from_obj(self, obj_file, output_file):
        # Open the .obj file and extract the data
        vertex_positions = []
        vertex_normals = []
        texture_coords = []
        faces = []
        
        # TODO: handle cases with w coordinates
        with open(obj_file, 'r') as f:
            # Iterate over each line in the .obj file
            for line in f:
                # Split the line into tokens
                tokens = line.split()
                # Check if the line is empty
                if len(tokens) == 0:
                    continue
                # Check if the line is a vertex position
                if tokens[0] == "v":
                    # Extract the x, y, and z coordinates
                    x, y, z = map(float, tokens[1:])
                    vertex_positions.append((x, y, z))
                # Check if the line is a vertex normal
                elif tokens[0] == "vn":
                    # Extract the x, y, and z components
                    x, y, z = map(float, tokens[1:])
                    vertex_normals.append((x, y, z))
                # Check if the line is a texture coordinate
                elif tokens[0] == "vt":
                    # Extract the u and v coordinates
                    u, v = map(float, tokens[1:])
                    texture_coords.append((u, v))
                # Check if the line is a face
                elif tokens[0] == "f":
                    # Extract the vertex indices
                    # TODO: handle nomal cords and other face formats
                    indices = [int(t.split("/")[0]) - 1 for t in tokens[1:]]
                    faces.append(indices)
                # Ignore other lines
        
        # prefix for the endianess
        prefix = "<" if self.endian == "little" else ">"

        # Open a binary file for writing
        with open(output_file, 'wb') as f:
            # Iterate over each block in the file format
            for block in self.blocks:
                # Iterate over each attribute in the block
                for att in block.attributes:
                    # Check the attribute name and write the corresponding data
                    if att.name == "position" or att.name == "vertex": # synonym
                        for pos in vertex_positions:
                            f.write(struct.pack(prefix + att.get_format_string(), *pos))
                    elif att.name == "normal":
                        for norm in vertex_normals:
                            f.write(struct.pack(prefix + att.get_format_string(), *norm))
                    elif att.name == "texcoord":
                        for tex in texture_coords:
                            f.write(struct.pack(prefix + att.get_format_string(), *tex))
                    elif att.name == "face":
                        for face in faces:
                            f.write(struct.pack(prefix + att.get_format_string(), *face))
                            print("face", face) # debug
                    elif len(att.name.split("_")) == 2 and att.name.split("_")[1] == "count":
                        print("registered a count attribute") # debug
                        if att.name.split("_")[0] == "vertex":
                            f.write(struct.pack(prefix + att.get_format_string(), len(vertex_positions)))
                            print("count vertex", len(vertex_positions)) # debug
                        elif att.name.split("_")[0] == "normal":
                            f.write(struct.pack(prefix + att.get_format_string(), len(vertex_normals)))
                        elif att.name.split("_")[0] == "texcoord":
                            f.write(struct.pack(prefix + att.get_format_string(), len(texture_coords)))
                        elif att.name.split("_")[0] == "face":
                            print("count faces", len(faces)) # debug
                            f.write(struct.pack(prefix + att.get_format_string(), len(faces)))
                    else:
                        # TODO: handle other attributes
                        f.write(struct.pack(prefix + att.get_format_string(), 0))
                        print("other", att.name, att.name.split("_")) # debug
                # Write the block terminator 
                if block.block_terminator is not None:
                    f.write(struct.pack(prefix + block.block_terminator.get_format_string(), 0))


    # Converts a binary file to a text file using the format specification
    # :param binary_file: Path to the binary file
    # :param output_file: Path to the output text file
    def binary_to_txt(self, binary_file, output_file):
        # prefix for the endianess
        prefix = "<" if self.endian == "little" else ">"
        indentation = 0
        # Open the binary file for reading
        with open(binary_file, 'rb') as f:
            # Open the output text file for writing
            with open(output_file, 'w') as out:
                # Write base information about the file format
                out.write(f"{' ' * indentation}File format: {self.name}\n")
                out.write(f"{' ' * indentation}Endianness: {self.endian}\n")
                out.write(f"\n")
                # Iterate over each block in the file format
                for block in self.blocks:
                    # Dictionary to store the count attributes for each block (key: attribute name, value: count)
                    count_dict = {}
                    # Write the base information about the block
                    out.write(f"{' ' * indentation}{block.name}:\n")
                    indentation += 2
                    # Iterate over each attribute in the block
                    for att in block.attributes:
                        # Check the attribute name and read the corresponding data
                        out.write(f"{' ' * indentation}{att.name}:\n")
                        indentation += 2
                        # extra check for the synonym "vertex" and "position"
                        special = False                                                                                 
                        if att.name == "position":
                            special = "vertex" in count_dict
                        # Check if the attribute is a dynamic attribute (e.g. position, normal, texcoord, face) 
                        if len(att.name.split("_")) == 1 and (att.name in count_dict or special):
                            # count exist for the current attribute
                            count = count_dict[att.name]
                            out.write(f"{' ' * indentation}[")
                            for i in range(count):
                                data = struct.unpack(prefix + att.get_format_string(), f.read(struct.calcsize(prefix + att.get_format_string())))
                                comma = ", " if i < count - 1 else ""
                                out.write(f"{data}{comma}")
                            out.write(f"]\n")
                        elif len(att.name.split("_")) == 2 and att.name.split("_")[1] == "count":
                            # Read the count attribute (count is always before the data)
                            data = struct.unpack(prefix + att.get_format_string(), f.read(struct.calcsize(prefix + att.get_format_string())))
                            out.write(f"{' ' * indentation}{data[0]}\n")
                            key = att.name.split("_")[0]
                            print(key)
                            if key == "position":
                                # vertex count is the same as position count
                                key = "vertex"
                                print("converted key to", key)
                            count_dict[key] = data[0]
                            
                        else:
                            # not a count or a dynamic attribute
                            data = struct.unpack(prefix + att.get_format_string(), f.read(struct.calcsize(prefix + att.get_format_string())))
                            if len(att.get_format_string()) > 1:
                                # attribute is a vector
                                out.write(f"{' ' * indentation}{data}\n")
                            else:
                                # attribute is a single value
                                out.write(f"{' ' * indentation}{data[0]}\n")
                            
                        indentation += -2
                    indentation += -2
                    # Empty line between blocks
                    out.write(f"\n")


    # Returns the combined format string for the entire file format
    def get_format_string(self):
        return ''.join(block.get_format_string() for block in self.blocks)


    def generate(self):
        pass