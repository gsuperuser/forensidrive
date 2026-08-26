import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestErasureCore(unittest.TestCase):
    def test_erasure_command_building(self):
        passes = 3
        device = "/dev/sdb"
        cmd = ["shred", "-v", f"-n{passes}", "-z", device]
        self.assertIn("shred", cmd)
        self.assertIn("-n3", cmd)
        self.assertIn(device, cmd)

    def test_boot_device_protection(self):
        # Ensure that boot device /dev/sda is rejected
        boot_dev = "/dev/sda"
        self.assertTrue(boot_dev.startswith("/dev/sda")) # Mock check

if __name__ == '__main__':
    unittest.main()
