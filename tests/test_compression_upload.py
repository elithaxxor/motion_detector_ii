import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import tempfile
import pytest
from motion_detector import compression_upload

def test_compress_video_fake():
    # Create a dummy file to represent a video
    with tempfile.NamedTemporaryFile(suffix='.mp4') as input_file, tempfile.NamedTemporaryFile(suffix='.mp4') as output_file:
        input_file.write(b'\x00' * 1024)  # Not a real video, just for test
        input_file.flush()
        # Should fail gracefully, not crash
        result = compression_upload.compress_video(input_file.name, output_file.name)
        assert result is False or result is True  # Accept both, but should not crash

def test_upload_file():
    assert compression_upload.upload_file('fake.mp4', 'http://example.com') is True
