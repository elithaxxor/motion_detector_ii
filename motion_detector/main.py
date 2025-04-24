"""
Main entry point for the YOLO-based Person Detection and Notification System.
- Detects humans in video/camera using YOLOv3-tiny.
- Shows live feed (GUI & web) only when a person is detected.
- Sends notifications (Email, Telegram, WhatsApp, Discord).
- Provides REST API for status and control.
"""
import sys
import os
import yaml
sys.path.insert(0, os.path.dirname(__file__))
import argparse
import threading
from utils import load_config, setup_logger, ensure_log_file
from motion import MotionDetector
from hotkey_listener import HotkeyListener
from auto_start import install_systemd_service, uninstall_systemd_service
from yolo_person_detector import YoloPersonDetector
from live_feed import LiveFeedManager
from notifier import Notifier
from api import APIServer
import cv2
import time

def main():
    """
    Main function to run the person detection system.
    Loads configuration, sets up detectors, hotkeys, notifications, and live feeds.
    """
    # Argument parsing for video file simulation
    parser = argparse.ArgumentParser(description='YOLO Person Detector')
    parser.add_argument('--video', type=str, default=None, help='Path to video file for simulation (instead of camera)')
    args = parser.parse_args()

    # Load config
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    cameras = config.get('cameras', [])

    for cam_cfg in cameras:
        # Each camera config now has its own settings and notifications
        sensitivity = cam_cfg.get('sensitivity', 800)
        threshold = cam_cfg.get('threshold', 100)
        hotkey = config.get('hotkey', 'ctrl+l')
        headless = config.get('headless', False)
        auto_start = config.get('auto_start', False)
        reference_update = cam_cfg.get('reference_update', True)
        camera_index = cam_cfg.get('camera_index', 0)
        log_file = cam_cfg.get('log_file', 'camera_log.txt')
        live_feed_timeout = cam_cfg.get('live_feed_timeout', 15)
        notifications_cfg = cam_cfg.get('notifications', {})
        # Extract configuration parameters
        email_notification = notifications_cfg.get('email', False)
        telegram_notification = notifications_cfg.get('telegram', False)
        whatsapp_notification = notifications_cfg.get('whatsapp', False)
        discord_notification = notifications_cfg.get('discord', False)

        # Ensure log file exists
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

        # Initialize notifier
        notifier = Notifier(config, email_notification, telegram_notification, whatsapp_notification, discord_notification)
        person_alert_sent = False

        # Initialize detectors
        detector = MotionDetector(sensitivity, threshold, reference_update, camera_index, logger, video_path=args.video)
        person_detector = YoloPersonDetector(conf_threshold=0.5)
        live_feed = LiveFeedManager()
        api_server = APIServer(detector, notifier, live_feed, stop_flag)
        api_server.start()

        # Open video capture
        cap = cv2.VideoCapture(args.video if args.video else camera_index)
        last_person_time = 0
        window_open = False
        live_feed_started = False

        try:
            while not stop_flag.is_set():
                # Read frame from video capture
                ret, frame = cap.read()
                if not ret:
                    break

                # Process frame for motion detection
                detected, out_frame, _, _ = detector.process_frame(frame)

                # Detect persons in the frame
                persons = person_detector.detect(frame)
                person_present = len(persons) > 0
                now = time.time()

                if person_present:
                    # Update last person time
                    last_person_time = now

                    # Send notification if not already sent
                    if not person_alert_sent:
                        url = f"http://localhost:5000/video_feed"
                        msg = f"Human detected! Live feed available at {url}"
                        notifier.notify_all("Human Detected", msg)
                        person_alert_sent = True

                    # Draw bounding boxes for detected persons
                    for (x1, y1, x2, y2, conf) in persons:
                        cv2.rectangle(out_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    # Start local GUI if not already open
                    if not window_open:
                        cv2.namedWindow('Live Feed', cv2.WINDOW_NORMAL)
                        window_open = True

                    # Display output frame
                    cv2.imshow('Live Feed', out_frame)

                    # Start web stream if not already running
                    if not live_feed_started:
                        live_feed.start()
                        live_feed_started = True

                    # Update live feed frame
                    live_feed.update_frame(out_frame)
                elif window_open and (now - last_person_time > live_feed_timeout):
                    # Close local GUI if live feed timeout exceeded
                    cv2.destroyWindow('Live Feed')
                    window_open = False
                elif live_feed_started and (now - last_person_time > live_feed_timeout):
                    # Stop web stream if live feed timeout exceeded
                    live_feed.stop()
                    live_feed_started = False
                    person_alert_sent = False

                # Hotkey and exit logic
                if window_open:
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        stop_flag.set()
                else:
                    if cv2.waitKey(1) == 27:
                        stop_flag.set()
        except KeyboardInterrupt:
            pass
        finally:
            # Release video capture and close windows
            cap.release()
            cv2.destroyAllWindows()

            # Stop live feed and API server
            if live_feed_started:
                live_feed.stop()
            api_server.stop()

            # Join hotkey listener thread
            hotkey_listener.join()

        print(f"Configured camera: {cam_cfg.get('name', camera_index)} with log {log_file}")
        # (For brevity, only config parsing is shown here; full refactor would loop detection logic per camera)

if __name__ == '__main__':
    main()