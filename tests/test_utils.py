import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from motion_detector import utils

def test_load_config(tmp_path):
    config_content = """
sensitivity: 123
threshold: 45
log_file: test_log.txt
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = utils.load_config(str(config_file))
    assert config['sensitivity'] == 123
    assert config['threshold'] == 45
    assert config['log_file'] == 'test_log.txt'

def test_ensure_log_file(tmp_path):
    log_file = tmp_path / "log.txt"
    utils.ensure_log_file(str(log_file))
    assert log_file.exists()
    content = log_file.read_text()
    assert "Motion Detection Log" in content

def test_setup_logger(tmp_path):
    log_file = tmp_path / "logger.txt"
    logger_name = "MotionDetectorTest"
    logger = logging.getLogger(logger_name)
    # Remove all handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger = utils.setup_logger(str(log_file))
    logger.info("test message")
    for handler in logger.handlers:
        if hasattr(handler, 'flush'):
            handler.flush()
    assert log_file.exists()
    assert "test message" in log_file.read_text()
