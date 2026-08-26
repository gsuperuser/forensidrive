import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestInspectionImports(unittest.TestCase):
    def test_import_inspection_ui(self):
        try:
            from app.modules.inspection.drive_details import DriveDetailsPage
            from app.modules.inspection.inspection import InspectionPage
            from app.modules.inspection.partition_details import PartitionDetailsPage
            self.assertTrue(hasattr(DriveDetailsPage, "__init__"))
            self.assertTrue(hasattr(InspectionPage, "__init__"))
            self.assertTrue(hasattr(PartitionDetailsPage, "__init__"))
        except ImportError as e:
            if 'tkinter' in str(e).lower() or '_tkinter' in str(e).lower():
                self.skipTest("Tkinter not available for UI test")
            else:
                self.fail(f"Failed to import inspection pages: {e}")

    def test_import_inspection_core(self):
        try:
            from app.core.storage import detect_drives, get_drive
            self.assertTrue(callable(detect_drives))
            self.assertTrue(callable(get_drive))
        except ImportError as e:
            self.fail(f"Failed to import storage core functions: {e}")

if __name__ == '__main__':
    unittest.main()
