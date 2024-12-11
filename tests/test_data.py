from data.file_formats import Attribute, Block, FormatSpec

def test1():
    # Define attributes for an simple example file format
    vertex_position = Attribute("position", "float", 3)
    vertex_count = Attribute("vertex_count", "uint32")
    face_indices = Attribute("face", "uint32", 3)
    face_count = Attribute("face_count", "uint32")

    # Define blocks for the example file format
    vertex_data_block = Block("vertex_data", [vertex_count, vertex_position])
    face_data_block = Block("face_data", [face_count, face_indices])

    # Define the file format specification
    example_format = FormatSpec("example", [vertex_data_block, face_data_block], "big")

    example_format.create_binary_from_obj("tests/testfiles/test.obj", "tests/testfiles/test.bin")

    example_format.binary_to_txt("tests/testfiles/test.bin", "tests/testfiles/test_converted.txt")

def test2():
    # Define attributes for an simple example file format
    vertex_count = Attribute("vertex_count", "uint16")
    vertex_position = Attribute("position", "float", 3)
    normal_count = Attribute("normal_count", "uint16")
    normal = Attribute("normal", "float", 3)
    texcoord_count = Attribute("texcoord_count", "uint16")
    texcoord = Attribute("texcoord", "float", 2)
    face_count = Attribute("face_count", "uint16")
    face = Attribute("face", "uint16", 3)
    face_normal = Attribute("face_normal", "uint16", 3)
    face_texcoord = Attribute("face_texcoord", "uint16", 3)

    # Define blocks for the example file format
    vertex_data_block = Block("vertex_data", [vertex_count, vertex_position, normal_count, normal, texcoord_count, texcoord])
    face_data_block = Block("face_data", [face_count, face, face_texcoord, face_normal])

    example_format = FormatSpec("example", [vertex_data_block, face_data_block], "big", "sequential")

    example_format.create_binary_from_obj("tests/testfiles/test2.obj", "tests/testfiles/test2.bin")

    example_format.binary_to_txt("tests/testfiles/test2.bin", "tests/testfiles/test2_converted.txt")
    
