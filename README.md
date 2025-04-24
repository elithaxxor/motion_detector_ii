# YOLO Persons Detector

A high-performance, privacy-respecting, on-demand live video feed and notification system for human detection using YOLOv3-tiny.

## Features
- **YOLOv3-tiny Person Detection:** Accurate detection of humans in camera/video streams.
- **On-Demand Live Feed:** Local GUI and web stream only appear when a person is detected.
- **Multi-Channel Notifications:** Email, Telegram, WhatsApp, Discord alerts with live feed link.
- **REST API:** Control and monitor the system via HTTP endpoints.
- **Hotkey Support:** Quickly stop or control the system via keyboard.
- **Extensible:** Modular codebase for multi-camera, cloud upload, face/object recognition, and more.

## Quick Start

### 1. Requirements
- Python 3.7+
- OpenCV (`opencv-python`)
- Flask
- requests

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Download YOLOv3-tiny Model Files
- Place `yolov3-tiny.cfg`, `yolov3-tiny.weights`, and `coco.names` in a `models/` directory at the project root.
- Download from [YOLO website](https://pjreddie.com/darknet/yolo/) or the [official repo](https://github.com/pjreddie/darknet/tree/master/cfg).

### 3. Configure Notifications
Edit `config.yaml` to enable and configure Email, Telegram, WhatsApp, and Discord notifications.

### 4. Run the Detector
```bash
python -m motion_detector.main
```

- The live feed (GUI and web at `http://localhost:5000/video_feed`) will activate only when a person is detected.
- Notifications are sent on detection.
- REST API available at `http://localhost:8000`.

## REST API
- `GET /status` — System status (live feed, detection active)
- `POST /notify` — Send notification (JSON: `{subject, body}`)
- `POST /control` — Start/stop detection (JSON: `{action: start|stop}`)

## File Structure
- `main.py` — Main entry point, orchestrates detection, feeds, notifications, API.
- `yolo_person_detector.py` — YOLOv3-tiny person detection logic.
- `live_feed.py` — Local GUI and Flask web stream.
- `notifier.py` — Notification logic for all channels.
- `api.py` — REST API server.
- `motion.py`, `hotkey_listener.py`, `auto_start.py`, `utils.py` — Utilities and support modules.

## Advanced Usage
- **Multi-camera:** Extend by running multiple pipelines or adding camera configs.
- **Cloud upload, face/object recognition:** Add new modules or models as needed.
- **Snapshot in notifications:** Easily extend notifier to send images.

## Security
- Protect `config.yaml` and model files.
- Use authentication for web/API if exposing beyond localhost.

## Contributing
Contributions welcome! Open issues or submit PRs for new features, bugfixes, or documentation.

## License
MIT License

---

**Repository:** https://github.com/elithaxxor/YOLO_Persons_Detector.git
