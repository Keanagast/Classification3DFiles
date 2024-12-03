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