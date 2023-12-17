import os
import unittest

import pb
MAGIC = 0xFFFFFFFF
DEVICE_APPS_TYPE = 1
TEST_FILE = "test.pb.gz"


class TestPB(unittest.TestCase):
    deviceapps = [
        {"device": {"type": "idfa", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7c"},
         "lat": 67.7835424444, "lon": -22.8044005471, "apps": [1, 2, 3, 4]},
        {"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"}, "lat": 42, "lon": -42, "apps": [1, 2]},
        {"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"}, "lat": 42, "lon": -42, "apps": []},
        {"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"}, "apps": [1]},
    ]

    def tearDown(self):
        os.remove(TEST_FILE)

    def test_write(self):
        bytes_written = pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        self.assertTrue(bytes_written > 0)
        
    def test_write_magic_str(self):
        pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        magic = struct.pack("I", MAGIC)
        with gzip.open(TEST_FILE, "rb") as file:
            magic_read = file.read(4)
            self.assertEqual(magic_read, self.magic)

    def test_message_invalid_type_dict(self):
        with self.assertRaises(TypeError):
            pb.deviceapps_xwrite_pb(["String", 11], TEST_FILE)

    def test_message_invalid_device(self):
        with self.assertRaises(TypeError):
            pb.deviceapps_xwrite_pb([{"device": 11, "lat": 42, "lon": -42, "apps": [1, 2]}], TEST_FILE)

    def test_message_invalid_device_type(self):
        with self.assertRaises(TypeError):
            pb.deviceapps_xwrite_pb([{"device": {"type": 321, "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"},\
                 "lat": 42, "lon": -42, "apps": [1, 2]}], TEST_FILE)
    
    def test_message_invalid_device_id(self):
        with self.assertRaises(TypeError):
            pb.deviceapps_xwrite_pb([{"device": {"type": "gaid", "id": 321},\
                 "lat": 42, "lon": -42, "apps": [1, 2]}], TEST_FILE)

    def test_message_invalid_lon_and_lat(self):
        with self.assertRaises(TypeError):
            pb.deviceapps_xwrite_pb({"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"},\
                 "lat": "42", "lon": -42, "apps": [1, 2]}, TEST_FILE)
        with self.assertRaises(TypeError):
            pb.deviceapps_xwrite_pb({"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"},\
                 "lat": 42, "lon": "-42", "apps": [1, 2]}, TEST_FILE)

    @unittest.skip("Optional problem")
    def test_read(self):
        pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        for i, d in enumerate(pb.deviceapps_xread_pb(TEST_FILE)):
            self.assertEqual(d, self.deviceapps[i])
