import os
import unittest
from struct import unpack
import gzip

import pb
from deviceapps import deviceapps_pb2


MAGIC = 0xFFFFFFFF
DEVICE_APPS_TYPE = 1
TEST_FILE = 'test.pb.gz'
HEADER_SIZE = 8


class TestPB(unittest.TestCase):
    deviceapps = [
        {'device': {'type': 'idfa', 'id': 'e7e1a50c0ec2747ca56cd9e1558c0d7c'},
         'lat': 67.7835424444, 'lon': -22.8044005471, 'apps': [1, 2, 3, 4]},
        {'device': {'type': 'gaid', 'id': 'e7e1a50c0ec2747ca56cd9e1558c0d7d'},
         'lat': 42, 'lon': -42, 'apps': [1, 2]},
        {'device': {'type': 'gaid', 'id': 'e7e1a50c0ec2747ca56cd9e1558c0d7d'},
         'lat': 42, 'lon': -42, 'apps': []},
        {'device': {'type': 'gaid', 'id': 'e7e1a50c0ec2747ca56cd9e1558c0d7d'},
         'apps': [1]},
        {'apps': []},
    ]

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_write_ok(self):
        bytes_written = pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        self.assertTrue(bytes_written > 0)

        with gzip.open(TEST_FILE) as f:
            for deviceapp in self.deviceapps:
                # Test header
                magic, device_apps_type, length = unpack('<IHH', f.read(HEADER_SIZE))
                self.assertEqual(magic, MAGIC)
                self.assertEqual(device_apps_type, DEVICE_APPS_TYPE)

                # Test body
                unpacked = deviceapps_pb2.DeviceApps()
                unpacked.ParseFromString(f.read(length))

                self.assertEqual(unpacked.device.id,
                                 deviceapp.get('device', {}).get('id', '').encode())
                self.assertEqual(unpacked.device.type,
                                 deviceapp.get('device', {}).get('type', '').encode())
                self.assertEqual(unpacked.lat,
                                 deviceapp.get('lat', 0))
                self.assertEqual(unpacked.lon,
                                 deviceapp.get('lon', 0))
                self.assertEqual(unpacked.apps,
                                 deviceapp.get('apps', []))

    def test_write_invalid_args_count(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb)
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, self.deviceapps)

    def test_write_invalid_iterable_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, 42, TEST_FILE)

    def test_write_invalid_filename_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, self.deviceapps, 42)

    def test_write_invalid_device_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, [
            {'device': 42},
        ], TEST_FILE)

    def test_write_invalid_device_id_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, [
            {'device': {'type': 'idfa', 'id': 42}},
        ], TEST_FILE)

    def test_write_invalid_device_type_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, [
            {'device': {'type': 42, 'id': 'e7e1a50c0ec2747ca56cd9e1558c0d7c'}},
        ], TEST_FILE)

    def test_write_invalid_lat_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, [
            {'lat': 'text'},
        ], TEST_FILE)

    def test_write_invalid_lon_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, [
            {'lon': 'text'},
        ], TEST_FILE)

    def test_write_invalid_apps_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, [
            {'apps': 42},
        ], TEST_FILE)

    def test_write_invalid_apps_item_type(self):
        self.assertRaises(TypeError, pb.deviceapps_xwrite_pb, [
            {'apps': ['text']},
        ], TEST_FILE)

    def test_write_invalid_file(self):
        self.assertRaises(OSError, pb.deviceapps_xwrite_pb, [], os.path.join(TEST_FILE, 'test'))

    def test_read_ok(self):
        pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        for i, d in enumerate(pb.deviceapps_xread_pb(TEST_FILE)):
            self.assertEqual(d, self.deviceapps[i])

    def test_read_invalid_args_count(self):
        pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        self.assertRaises(TypeError, pb.deviceapps_xread_pb)

    def test_read_invalid_file(self):
        self.assertRaises(OSError, pb.deviceapps_xread_pb, TEST_FILE)
