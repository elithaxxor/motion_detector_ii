import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import cv2
import pytest
from motion_detector.motion import MotionDetector
import logging

def dummy_logger():
    logger = logging.getLogger('dummy')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    return logger

def test_process_frame_no_motion():
    detector = MotionDetector(800, 100, True, 0, dummy_logger())
    frame = np.zeros((500, 500, 3), dtype=np.uint8)
    detected, out_frame, dilated, frame_delta = detector.process_frame(frame)
    assert detected is False
    assert out_frame is not None
    assert dilated is None
    assert frame_delta is None

def test_process_frame_with_motion():
    detector = MotionDetector(100, 50, True, 0, dummy_logger())
    frame1 = np.zeros((500, 500, 3), dtype=np.uint8)
    frame2 = frame1.copy()
    cv2.rectangle(frame2, (100, 100), (200, 200), (255, 255, 255), -1)
    detector.process_frame(frame1)
    detected, out_frame, dilated, frame_delta = detector.process_frame(frame2)
    assert detected is True
    assert out_frame is not None
    assert dilated is not None
    assert frame_delta is not None
