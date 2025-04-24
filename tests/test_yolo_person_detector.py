import unittest
import numpy as np
from motion_detector.yolo_person_detector import YoloPersonDetector

class TestYoloPersonDetector(unittest.TestCase):
    def setUp(self):
        # Use a dummy model directory or mock for real tests
        self.detector = YoloPersonDetector(model_dir="../models")

    def test_detect_blank_image(self):
        # Blank image should not detect any persons
        img = np.zeros((416, 416, 3), dtype=np.uint8)
        results = self.detector.detect(img)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
