import threading
import os
import sys
import argparse
from utils import load_config, setup_logger, ensure_log_file
from motion import MotionDetector
from hotkey_listener import HotkeyListener
from auto_start import install_systemd_service, uninstall_systemd_service

if __name__ == '__main__':
    # Argument parsing for video file simulation
    parser = argparse.ArgumentParser(description='Motion Detector')
    parser.add_argument('--video', type=str, default=None, help='Path to video file for simulation (instead of camera)')
    args = parser.parse_args()

    # Load config
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config = load_config(config_path)
    
    sensitivity = config.get('sensitivity', 800)
    threshold = config.get('threshold', 100)
    hotkey = config.get('hotkey', 'ctrl+l')
    headless = config.get('headless', False)
    auto_start = config.get('auto_start', False)
    reference_update = config.get('reference_update', True)
    camera_index = config.get('camera_index', 0)
    log_file = config.get('log_file', 'camera_log.txt')

    ensure_log_file(log_file)
    logger = setup_logger(log_file)

    # Handle auto-start setup
    if '--install-autostart' in sys.argv:
        install_systemd_service('motion_detector', os.path.abspath(__file__))
        sys.exit(0)
    if '--uninstall-autostart' in sys.argv:
        uninstall_systemd_service('motion_detector')
        sys.exit(0)

    # Prepare stop flag for clean exit
    stop_flag = threading.Event()
    hotkey_listener = HotkeyListener(hotkey, stop_flag)
    hotkey_listener.start()

    detector = MotionDetector(sensitivity, threshold, reference_update, camera_index, logger, video_path=args.video)
    try:
        detector.run(hotkey, headless, log_file, stop_flag)
    except KeyboardInterrupt:
        print('Interrupted by user.')
    finally:
        hotkey_listener.stop()
        print('Motion detector stopped.')