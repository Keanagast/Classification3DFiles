import tests.test_data as test_data
import struct

test_data.test1()

test_data.test2()

# test = "test"
# print(f"Test: {test} {test.split("_")}")

# test = test.encode("utf-8")
# pre = struct.pack("H", len(test))
# print(f"Only encoding: {test} \n With prefix: {pre + test}")

# with open("tests/testfiles/StringTest.bin", "wb") as f:
#     f.write(pre + test)

# test2 = "10/78/93"
# test3 = "10//93"
# test4 = "10"
# if "//" in test2:
#     print("Found // in test2")

# if "//" in test3:
#     print("Found // in test3")

# if "//" in test4:
#     print("Found // in test4")
    
# print(f"Test2: {test2.split('//')}, {test2.split('/')}")
# print(f"Test3: {test3.split('//')}, {test3.split('/')}")