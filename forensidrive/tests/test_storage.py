import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.drive import Drive
from app.models.partition import Partition
from unittest.mock import patch

class TestStorageModels(unittest.TestCase):
    def setUp(self):
        self.sample_drive_data = {
            "name": "sda",
            "size": "500G",
            "type": "disk",
            "mountpoint": None,
            "fstype": None,
            "children": [
                {
                    "name": "sda1",
                    "size": "500M",
                    "type": "part",
                    "mountpoint": "/boot/efi",
                    "fstype": "vfat"
                },
                {
                    "name": "sda2",
                    "size": "499.5G",
                    "type": "part",
                    "mountpoint": "/",
                    "fstype": "ext4"
                }
            ]
        }

    def test_drive_from_lsblk_dict(self):
        drive = Drive.from_lsblk_dict(self.sample_drive_data)
        self.assertEqual(drive.name, "sda")
        self.assertEqual(drive.size, "500G")
        self.assertEqual(drive.type, "disk")
        self.assertEqual(len(drive.partitions), 2)
        self.assertEqual(drive.partitions[0].name, "sda1")

    def test_drive_display_name(self):
        drive = Drive.from_lsblk_dict(self.sample_drive_data)
        self.assertEqual(drive.display_name, "sda - 500G (2 partitions)")

    def test_drive_human_size(self):
        self.assertEqual(Drive.human_size(1024), "1.0 KB")
        self.assertEqual(Drive.human_size(1048576), "1.0 MB")
        self.assertEqual(Drive.human_size(1073741824), "1.0 GB")

    def test_partition_from_lsblk_dict(self):
        part_data = self.sample_drive_data["children"][1]
        partition = Partition.from_lsblk_dict(part_data, parent_drive_name="sda")
        self.assertEqual(partition.name, "sda2")
        self.assertEqual(partition.size, "499.5G")
        self.assertEqual(partition.mountpoint, "/")
        self.assertEqual(partition.fstype, "ext4")
        self.assertEqual(partition.parent_drive_name, "sda")

    def test_partition_is_mounted(self):
        part_data = self.sample_drive_data["children"][1]
        partition = Partition.from_lsblk_dict(part_data, parent_drive_name="sda")
        self.assertTrue(partition.is_mounted)
        
        part_data_unmounted = {"name": "sdb1", "size": "10G", "type": "part", "mountpoint": None, "fstype": "ext4"}
        partition_unmounted = Partition.from_lsblk_dict(part_data_unmounted, parent_drive_name="sdb")
        self.assertFalse(partition_unmounted.is_mounted)

if __name__ == '__main__':
    unittest.main()
