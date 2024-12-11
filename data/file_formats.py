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
    # :param endian: Endianness of the file format (default is "little", can be "big")
    # :param face_format: Format of the face data (default is "sequential", can be "seperate")
    def __init__(self, name, blocks = [], endian = "little", face_format = "sequential"):
        self.name = name
        self.blocks = blocks
        # check if endian is valid
        if endian in ["little", "big"]:
            self.endian = endian
        else:
            self.endian = "little"
            raise ValueError(f"Invalid endianness: {endian}")
        # check if face format is valid
        if face_format in ["sequential", "seperate"]:
            self.face_format = face_format
        else:
            self.face_format = "sequential"
            raise ValueError(f"Invalid face format: {face_format}")
        

    # Adds a block to the file format
    # :param block: Block to add
    def add_block(self, block):
        self.blocks.append(block)

    # Converts a .obj file to a binary file using the format specification
    # :param obj_file: Path to the .obj file
    def create_binary_from_obj(self, obj_file, output_file):
        # Open the .obj file and extract the data

        # Lists to store the vertex positions, normals, texture coordinates, and faces
        # length of faces, face_normals and face_texcoords is the same and the same index refrences the same face
        vertex_positions = []
        vertex_normals = []
        texture_coords = []

        faces = []
        face_normals = []
        face_texcoords = []
        
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
                    #check what case this is
                    if "//" in tokens[1]:
                        # case with only vertex and normal indices
                        # indices are atleast 1, if it is 0, it indicates a empty input
                        indices = [int(t.split("//")[0]) for t in tokens[1:]]
                        faces.append(indices)
                        # add normal indices
                        indices = [int(t.split("//")[1]) for t in tokens[1:]]
                        face_normals.append(indices)
                        # add a placeholder for texture indices
                        indices = [0 for t in tokens[1:]]
                        face_texcoords.append(indices)
                    elif "/" in tokens[1]:
                        # case with atleast vertex, texture
                        indices = [int(t.split("/")[0]) for t in tokens[1:]]
                        faces.append(indices)
                        # add texture indices
                        indices = [int(t.split("/")[1]) for t in tokens[1:]]
                        face_texcoords.append(indices)
                        # check if there are normal indices
                        if len(tokens[1].split("/")) > 2:
                            indices = [int(t.split("/")[2]) for t in tokens[1:]]
                        else:
                            indices = [0 for t in tokens[1:]]
                        face_normals.append(indices)
                    else:
                        # case with only vertex indices
                        indices = [int(t.split("/")[0]) for t in tokens[1:]]
                        faces.append(indices)
                        # add a placeholder for texture and normal indices
                        indices = [0 for t in tokens[1:]]
                        face_texcoords.append(indices)
                        face_normals.append(indices)
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
                        # if the face format is sequential and this is not the first attribute in the list of attributes then the face data is already written and therefore the list is empty
                        # if the face format is seperate then the face data is written here
                        for i,face in enumerate(faces):
                            f.write(struct.pack(prefix + att.get_format_string(), *face))
                            print("face", face) # debug
                            # check if face format is sequential or seperate
                            if self.face_format == "sequential":
                                # go through all block attributes and write the corresponding data for the texture and normal indices
                                count = 0
                                for att2 in block.attributes:
                                    if att2.name == "face_normal":
                                        # write the normal indices
                                        norm = face_normals[i]
                                        f.write(struct.pack(prefix + att2.get_format_string(), *norm))
                                        print("face normal", norm) # debug
                                        count += 1
                                        # break if both normal and texture indices are written
                                        if count == 2:
                                            break
                                    elif att2.name == "face_texcoord":
                                        # write the texture indices
                                        tex = face_texcoords[i]
                                        f.write(struct.pack(prefix + att2.get_format_string(), *tex))
                                        print("face texcoord", tex)
                                        count += 1
                                        if count == 2:
                                            break
                        if self.face_format == "sequential":
                            # empty lists so it wont be written again for the seperate format code
                            face_normals = []
                            face_texcoords = []
                    elif att.name == "face_normal":
                        for i,norm in enumerate(face_normals):
                            f.write(struct.pack(prefix + att.get_format_string(), *norm))
                            print("face normal", norm) # debug
                            # check if face format is sequential or seperate
                            if self.face_format == "sequential":
                                # go through all block attributes and write the corresponding data for the texture and face indices
                                count = 0
                                for att2 in block.attributes:
                                    if att2.name == "face_texcoord":
                                        # write the texture indices
                                        tex = face_texcoords[i]
                                        f.write(struct.pack(prefix + att2.get_format_string(), *tex))
                                        print("face texcoord", tex)
                                        count += 1
                                        if count == 2:
                                            break
                                    elif att2.name == "face":
                                        face = faces[i]
                                        f.write(struct.pack(prefix + att2.get_format_string(), *face))
                                        print("face", face)
                                        count += 1
                                        if count == 2:
                                            break
                        if self.face_format == "sequential":
                            # empty lists so it wont be written again for the seperate format code
                            faces = []
                            face_texcoords = []
                    elif att.name == "face_texcoord":
                        for i,tex in enumerate(face_texcoords):
                            f.write(struct.pack(prefix + att.get_format_string(), *tex))
                            print("face texcoord", tex) # debug
                            # check if face format is sequential or seperate
                            if self.face_format == "sequential":
                                # go through all block attributes and write the corresponding data for the normal and face indices
                                count = 0
                                for att2 in block.attributes:
                                    if att2.name == "face_normal":
                                        norm = face_normals[i]
                                        f.write(struct.pack(prefix + att2.get_format_string(), *norm))
                                        print("face normal", norm)
                                        count += 1
                                        if count == 2:
                                            break
                                    elif att2.name == "face":
                                        face = faces[i]
                                        f.write(struct.pack(prefix + att2.get_format_string(), *face))
                                        print("face", face)
                                        count += 1
                                        if count == 2:
                                            break
                        if self.face_format == "sequential":
                            # empty lists so it wont be written again for the seperate format code
                            faces = []
                            face_normals = []
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
                    elif att.type == "string":
                        # TODO: where to get string attribute from?
                        # string attribute is most likely not used as a type
                        placeholder = "test"
                        packed_string = pack_string(placeholder, prefix + att.get_format_string(), "utf-8")
                        f.write(packed_string)
                    else:
                        # TODO: handle other attributes
                        f.write(struct.pack(prefix + att.get_format_string(), 0))
                        #print("other", att.name, att.name.split("_")) # debug
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
                    done_sequentail = False
                    # Dictionary to store the count attributes for each block (key: attribute name, value: count)
                    count_dict = {}
                    # Write the base information about the block
                    out.write(f"{' ' * indentation}{block.name}:\n")
                    indentation += 2
                    # Iterate over each attribute in the block
                    for att in block.attributes:
                        # Check the attribute name and read the corresponding data
                        if att.name in ["face", "face_normal", "face_texcoord"]:
                            if not done_sequentail:
                                out.write(f"{' ' * indentation}{att.name}:\n")
                        else:
                            out.write(f"{' ' * indentation}{att.name}:\n")
                        indentation += 2
                        # extra check for the synonym "vertex" and "position"                                                                             
                        if att.name == "position":
                            key = "vertex"
                        else:
                            key = att.name
                        # Check if the attribute is a dynamic attribute (e.g. position, normal, texcoord, face) 
                        if key in count_dict and (not done_sequentail or att.name not in ["face", "face_normal", "face_texcoord"]):
                            # count exist for the current attribute
                            count = count_dict[key]
                            out.write(f"{' ' * indentation}[")
                            # lists in case of sequential face format
                            face = []
                            face_normal = []
                            face_texcoord = []
                            for i in range(count):
                                # if sequential face format, skip the for loop
                                if att.name in ["face", "face_normal", "face_texcoord"]:
                                    if not done_sequentail:
                                        data = struct.unpack(prefix + att.get_format_string(), f.read(struct.calcsize(prefix + att.get_format_string())))
                                    else:
                                        break
                                else:
                                    data = struct.unpack(prefix + att.get_format_string(), f.read(struct.calcsize(prefix + att.get_format_string())))

                                # Check if the attribute is apart of the face data and the face format is sequential
                                if att.name in ["face", "face_normal", "face_texcoord"] and self.face_format == "sequential":
                                    # Store the data in a list
                                    for att2 in block.attributes:
                                        if att2.name == "face" and att2.name != att.name:
                                            print("face unpack string: ", prefix + att2.get_format_string(), " size: ", struct.calcsize(prefix + att2.get_format_string()))
                                            data2 = struct.unpack(prefix + att2.get_format_string(), f.read(struct.calcsize(prefix + att2.get_format_string())))
                                            face.append(data2)
                                        elif att2.name == "face_normal" and att2.name != att.name:
                                            data2 = struct.unpack(prefix + att2.get_format_string(), f.read(struct.calcsize(prefix + att2.get_format_string())))
                                            face_normal.append(data2)
                                        elif att2.name == "face_texcoord" and att2.name != att.name:
                                            data2 = struct.unpack(prefix + att2.get_format_string(), f.read(struct.calcsize(prefix + att2.get_format_string())))
                                            face_texcoord.append(data2)
                                
                                comma = ", " if i < count - 1 else ""
                                out.write(f"{data}{comma}")
                            out.write(f"]\n")
                            if self.face_format == "sequential" and not done_sequentail:
                                names = [att2.name for att2 in block.attributes]
                                # Write the 2 other attributes if they exist
                                if "face" in names and att.name != "face":
                                    out.write(f"{' ' * (indentation-2)}face:\n{' '*indentation}{face}\n")
                                if "face_normal" in names and att.name != "face_normal":
                                    out.write(f"{' ' * (indentation-2)}face_normal:\n{' '*indentation}{face_normal}\n")
                                if "face_texcoord" in names and att.name != "face_texcoord":
                                    out.write(f"{' ' * (indentation-2)}face_texcoord:\n{' '*indentation}{face_texcoord}\n")
                                done_sequentail = True
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
                            elif key == "face":
                                # face count is the same as face normal count and face texcoord count -> add both to the dictionary
                                count_dict["face_normal"] = data[0]
                                count_dict["face_texcoord"] = data[0]
                            count_dict[key] = data[0]
                        elif att.type == "string":
                            # Read the string attribute 
                            data = unpack_string(f, prefix + att.get_format_string(), "utf-8")
                            out.write(f"{' ' * indentation}{data}\n")
                        elif att.name not in ["face", "face_normal", "face_texcoord"]:
                            # not a dynamic attribute, a count or a string
                            print("not a dynamic attribute, a count or a string", att.name, count_dict)
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