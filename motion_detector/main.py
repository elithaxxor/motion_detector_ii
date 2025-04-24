import threading
import os
import sys
import argparse
from utils import load_config, setup_logger, ensure_log_file
from motion import MotionDetector
from hotkey_listener import HotkeyListener
from auto_start import install_systemd_service, uninstall_systemd_service
from person_detector import PersonDetector
from live_feed import LiveFeedManager
from notifier import Notifier
import cv2
import time

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
    live_feed_timeout = config.get('live_feed_timeout', 15)  # seconds

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

    notifier = Notifier(config)
    person_alert_sent = False

    detector = MotionDetector(sensitivity, threshold, reference_update, camera_index, logger, video_path=args.video)
    person_detector = PersonDetector()
    live_feed = LiveFeedManager()

    cap = cv2.VideoCapture(args.video if args.video else camera_index)
    last_person_time = 0
    window_open = False
    live_feed_started = False

    try:
        while not stop_flag.is_set():
            ret, frame = cap.read()
            if not ret:
                break
            detected, out_frame, _, _ = detector.process_frame(frame)
            persons = person_detector.detect(frame)
            person_present = len(persons) > 0
            now = time.time()

            if person_present:
                last_person_time = now
                if not person_alert_sent:
                    url = f"http://localhost:5000/video_feed"
                    msg = f"Human detected! Live feed available at {url}"
                    notifier.notify_all("Human Detected", msg)
                    person_alert_sent = True
                # Draw boxes
                for (x1, y1, x2, y2, conf) in persons:
                    cv2.rectangle(out_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                # Start local GUI if not already open
                if not window_open:
                    cv2.namedWindow('Live Feed', cv2.WINDOW_NORMAL)
                    window_open = True
                cv2.imshow('Live Feed', out_frame)
                # Start web stream if not already running
                if not live_feed_started:
                    live_feed.start()
                    live_feed_started = True
                live_feed.update_frame(out_frame)
            elif window_open and (now - last_person_time > live_feed_timeout):
                cv2.destroyWindow('Live Feed')
                window_open = False
            elif live_feed_started and (now - last_person_time > live_feed_timeout):
                live_feed.stop()
                live_feed_started = False
                person_alert_sent = False

            if window_open:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    stop_flag.set()
            else:
                if cv2.waitKey(1) == 27:
                    stop_flag.set()
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if live_feed_started:
            live_feed.stop()
        hotkey_listener.join()