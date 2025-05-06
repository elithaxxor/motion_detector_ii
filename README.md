# YOLO Persons Detector

## [2025-05-06] Update
- Documentation reviewed and updated for clarity and completeness.
- Installation, usage, and testing instructions improved.
- C++ and Python integration details clarified.
- Added troubleshooting for common issues (e.g., OpenCV install).
- Updated YOLO_EMBEDDED section for embedded/edge use cases.

A high-performance, privacy-respecting, on-demand live video feed and notification system for human detection using YOLOv3-tiny.

## Changelog
See [CHANGELOG.md](./CHANGELOG.md) for a detailed list of changes and release notes.

## Features
- **YOLOv3-tiny Person Detection:** Accurate detection of humans in camera/video streams.
- **On-Demand Live Feed:** Local GUI and web stream only appear when a person is detected.
- **Multi-Channel Notifications:** Email, Telegram, WhatsApp, Discord alerts with live feed link.
- **REST API:** Control and monitor the system via HTTP endpoints.
- **Hotkey Support:** Quickly stop or control the system via keyboard.
- **Extensible:** Modular codebase for multi-camera, cloud upload, face/object recognition, and more.
- **.env file for API keys**: Store Telegram, WhatsApp, Discord, and Shodan API keys securely.
- **Shodan API integration**: Query Shodan for device exposure and enrich alerts.
- **Remote access**: The dashboard and API can be accessed remotely (listens on 0.0.0.0).
- **C code organization**: All C code moved to `YOLO_EMBEDDED/` directory.

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

## Instructions for Remote Access & Security

1. **Start the server:**
   ```bash
   python3 motion_detector/main.py
   ```
2. **Firewall:**
   - Ensure your firewall allows inbound connections on the port you run the server (default: 5000).
   - For Linux with ufw:
     ```bash
     sudo ufw allow 5000
     ```
3. **Access Remotely:**
   - From any device/browser on your network (or Internet, if port forwarded), visit:
     ```
     http://<your-server-ip>:5000
     ```
4. **Security:**
   - Do NOT share your .env or config.yaml files.
   - For Internet exposure, use authentication, VPN, or firewall rules for safety.

## .gitignore Usage
- A `.gitignore` file is provided to prevent sensitive files from being committed to git.
- By default, `.env`, log files, and other secrets are excluded from version control.

## Remote Access
To access the dashboard and API remotely:
1. Make sure your server firewall allows inbound connections on the relevant port (default: 5000 or 8000).
2. Start the server with:
   ```bash
   python3 motion_detector/main.py
   ```
3. Visit `http://<your-server-ip>:5000` or `http://<your-server-ip>:8000` from your remote device/browser.

## Environment Variables (.env)
Create a `.env` file in your project root:
```
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
WHATSAPP_PHONE=your_whatsapp_phone
WHATSAPP_APIKEY=your_whatsapp_apikey
DISCORD_WEBHOOK_URL=your_discord_webhook
SHODAN_API_KEY=your_shodan_api_key
```

## Shodan API Usage
You can use Shodan utilities in your code:
```python
from motion_detector.shodan_utils import shodan_search, shodan_host
results = shodan_search('webcam')
print(results)
```

## YOLO_EMBEDDED

YOLO_EMBEDDED is a module for embedded object/person detection using the YOLO (You Only Look Once) algorithm. It is designed for efficient real-time detection on security camera feeds or other video sources.

### Features
- Real-time person detection using YOLO
- Region of interest (ROI) selection
- Motion detection
- Notification support

### Installation

#### Prerequisites
- Python 3.7+
- pip
- OpenCV (cv2)
- numpy
- Flask (if using the web interface)
- [Optional] ffmpeg (for video processing)

#### Install Python dependencies
```sh
pip install -r requirements.txt
```

#### Install OpenCV
```sh
pip install opencv-python
```

#### C++ Components
If using C++ modules (e.g., roi_select.cpp):
```sh
g++ roi_select.cpp -o roi_select `pkg-config --cflags --libs opencv4`
```

### Usage
- Run the main Python module:
```sh
python3 motion_detector/main.py
```
- For C++ ROI selection:
```sh
./roi_select
```

### Configuration
- Edit the `.env` file for environment variables.
- Camera sources and notification settings can be adjusted in the configuration files.

### Testing
To run all Python tests:
```sh
pytest
```

### Project Structure
- `motion_detector/`: Main Python code for motion and person detection
- `tests/`: Test suite
- `roi_select.cpp`: C++ ROI selection tool

### License
See LICENSE file for details.

## File Structure
- `main.py` — Main entry point, orchestrates detection, feeds, notifications, API.
- `yolo_person_detector.py` — YOLOv3-tiny person detection logic.
- `live_feed.py` — Local GUI and Flask web stream.
- `notifier.py` — Notification logic for all channels.
- `api.py` — REST API server.
- `motion.py`, `hotkey_listener.py`, `auto_start.py`, `utils.py` — Utilities and support modules.
- `YOLO_EMBEDDED/` — Directory containing all C code.

## Advanced Usage
- **Multi-camera:** Extend by running multiple pipelines or adding camera configs.
- **Cloud upload, face/object recognition:** Add new modules or models as needed.
- **Snapshot in notifications:** Easily extend notifier to send images.

## Security
- Protect `config.yaml` and model files.
- Use authentication for web/API if exposing beyond localhost.
- Protect your .env and config.yaml files. Do not share them publicly.
- For remote access, ensure you use strong passwords and consider VPN or firewall restrictions.

## Contributing
Contributions welcome! Open issues or submit PRs for new features, bugfixes, or documentation.

## License
MIT License

---

**Repository:** https://github.com/elithaxxor/YOLO_Persons_Detector.git
