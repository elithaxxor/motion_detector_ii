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
- **Advanced ML Models**: Support for newer YOLOv5/v8 models for multi-class detection (vehicles, animals) and face recognition for known-person alerts.
  
### Supported Detector Models

This system can be configured to use two classes of object/person detectors:

1. **YOLOv3-tiny (default):**
   - Uses OpenCV’s DNN module to load Darknet `.cfg` and `.weights` files.
   - Very lightweight (~7M parameters) with two detection heads (13×13, 26×26 feature maps).
   - Excellent CPU-only performance (≈30–60 FPS) at the cost of accuracy (≈20–30 mAP on COCO).
   - No extra deep-learning dependencies beyond OpenCV.

2. **YOLOv5/v8 (via `ultralytics`):**
   - Modern PyTorch models (20–100M+ parameters) with CSP backbones and PANet necks.
   - Supports GPU acceleration, mixed-precision, batching, and advanced training scripts.
   - Higher accuracy (≈30–50 mAP on COCO; varies by model size).
   - Exportable to ONNX, TensorFlow, TFLite; easily fine-tunable on custom datasets.
   - Requires installing `torch` and `ultralytics`.

## YOLOv5/v8 Model Weights
To use YOLOv5 or YOLOv8 models in this system, you need a pre-trained model weights file (a `.pt` file). This file contains the learned parameters of the YOLO model and is essential for the detector to function.

A “.pt” file in this context is simply a PyTorch weights file—i.e. the learned parameters for a YOLOv5 (or v8) model.  There are two common ways to get one:

    1. Grab a **pre-trained** checkpoint from Ultralytics
       • Install the ultralytics package:

           pip install ultralytics

       • Make a `models/` folder at your project root (if you haven’t already):

           mkdir -p models

       • Download the small YOLOv5 weights directly into it:

           wget https://github.com/ultralytics/yolov5/releases/download/v8.0/yolov5s.pt -P models/

       • Now you’ll have `models/yolov5s.pt`, and our config’s

           detector:
             type: yolo_v5
             model_path: models/yolov5s.pt
             …

         will load that model exactly.
    2. **Train your own** custom YOLOv5/v8 model and export it to a .pt file
       a) Clone the YOLOv5 repo and install its requirements:

           git clone https://github.com/ultralytics/yolov5.git
           cd yolov5
           pip install -r requirements.txt

       b) Prepare a `data.yaml` for your dataset (YOLO format, with train/val paths and class names).
       c) Train:

           python train.py \
             --img 640 \
             --batch 16 \
             --epochs 50 \
             --data path/to/data.yaml \
             --weights yolov5s.pt        # start from the small pre-trained model

       d) When training finishes, your best weights will live in something like
          `yolov5/runs/train/exp/weights/best.pt`
       e) Copy or move that into your project’s `models/` directory and update `model_path` in `config.yaml` accordingly.

Once you have a .pt file in models/, our AdvancedYOLODetector will load it automatically.
To select between them, add or modify the `detector` block in your `config.yaml`:
```yaml
detector:
  type: yolo_v5   # or 'yolo_v8'; falls back to yolo_v3 (tiny) if missing or unavailable
  model_path: models/yolov5s.pt
  conf_threshold: 0.5
  target_classes:
    - person
    - car
    - bicycle
```

## Quick Start

This guide provides a quick setup for the YOLO Persons Detector, including installation, configuration, and running the system.
To get everything rolling:

    1. **Put your .pt weights into models/**
       You need a YOLOv5/V8 weights file (PyTorch `.pt`). For example:
       - **Download a pretrained YOLOv5s model:**
         ```bash
         mkdir -p models
         wget -P models https://github.com/ultralytics/yolov5/releases/download/v6.2/yolov5s.pt
         ```
       - **Or download a pretrained YOLOv8n model:**
         ```bash
         wget -P models https://github.com/ultralytics/ultralytics/releases/download/v8.0/yolov8n.pt
         ```
       - **Or train your own custom model** via the Ultralytics repo (`train.py`), then copy `runs/train/exp/weights/best.pt` into `models/`.
    2. **Edit config.yaml’s detector: block**
       Under each camera, configure:

           detector:
             type: yolo_v5      # or yolo_v8
             model_path: models/yolov5s.pt
             conf_threshold: 0.5
             target_classes:
               - person
               - car
               - bicycle

       Adjust `model_path`, `conf_threshold` and `target_classes` as needed.

       3. Set the password and secret key for the dashboard in `config.yaml`, or by     

    # 1) Override the dashboard login password (defaults to “admin”):
    export DASHBOARD_PASSWORD=mySuperSecretPassword

    # 2) Override the Flask session secret key
    #    (defaults to “change_this_in_production” if you don’t set it)
    export DASHBOARD_SECRET_KEY=myDifferentSecretKey

 

           dashboard:
             password: your_password_here
             secret_key: your_secret_key_here
    4. **(Optional) Fill known_faces/**
       • Create a `known_faces/` directory at the project root.
       • Drop in labeled images (e.g. `Alice.jpg`, `Bob.png`).
       • If you skip this, face‐recognition simply won’t run, but unknown faces will now be auto‐learned and labeled on first sight!
       
    5. **Run the detector**

           python -m motion_detector.main

       Every time a new face appears (beyond your static `known_faces/`), the system will crop it, assign a new label (e.g. `Person_001`) and persist that encoding—so next time it’ll recognize it automatically.

    5. **View the interfaces**
       - **Live Feed** on port 3000: http://localhost:3000/  (serves a simple page with the MJPEG stream)
       - **Dashboard & API** on port 3001: http://localhost:3001/  (redirects to `/dashboard/login`)
       - **Detection Log**: check `motiondetection.log` at the project root for timestamped detection events

To run the detector from your project root:

    1. Open a terminal and `cd` into the project directory:

           cd /path/to/motion_detector_ii-main
    2. (Optional but recommended) Create and activate a Python virtual environment:

           python3 -m venv .venv
           source .venv/bin/activate
    3. Install all required Python packages:

           pip install -r requirements.txt
    4. Make sure you’ve placed your YOLO weights (e.g. `yolov5s.pt`) in `models/` and configured the `detector:` block in `config.yaml`.
    5. (Optional) If you want face recognition, create a `known_faces/` folder at the project root and drop in labeled images (e.g. `Alice.jpg`, `Bob.png`). If you skip this, face-recog will simply be disabled.
    6. Launch the detector:

           python -m motion_detector.main

       • To test against a video file instead of a live camera, add `--video`:

           python -m motion_detector.main --video path/to/file.mp4
    7. You’ll see a GUI window pop up (when motion + person is detected), and the web stream will be available at

           http://localhost:3000/video_feed

       Alerts (with recognized-face names, or generated labels like `Person_001`) will be sent via your configured notification channels.


“YOLO weights” refers to the file that contains a pretrained YOLO network’s learned parameters.  When you train or download a YOLOv5/v8 model, you get a .pt file (a PyTorch checkpoint) such as yolov5s.pt,
yolov5m.pt, or one you’ve exported yourself after training on a custom dataset.

By putting that file in a folder named models/ at the root of this project, our AdvancedYOLODetector can load it with a single line:

    from ultralytics import YOLO
    model = YOLO("models/yolov5s.pt")


### How to organize your models/ folder

Your project tree should look roughly like:

    motion_detector_ii-main/
    ├── models/
    │   └── yolov5s.pt         ← your YOLOv5/v8 weights
    ├── known_faces/
    ├── motion_detector/
    ├── config.yaml
    ├── requirements.txt
    └── README.md

    If you still want to use the built-in YOLOv3-tiny detector, drop the 3 files there instead:
    
        * `models/yolov3-tiny.cfg`
        * `models/yolov3-tiny.weights`
        * `models/coco.names`


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

- The live feed (GUI and web at `http://localhost:3000/video_feed`) will activate only when a person is detected.
- Notifications are sent on detection.
- REST API available at `http://localhost:3001`.
  
### Advanced ML Models Usage

To use YOLOv5/v8 for multi-class detection:
1. Ensure additional dependencies are installed (`torch`, `ultralytics`, `face_recognition`):
   ```bash
   pip install -r requirements.txt
   ```
2. In each camera section of `config.yaml`, add a `detector` block:
   ```yaml
   detector:
     type: yolo_v5   # or yolo_v8
     model_path: models/yolov5s.pt
     conf_threshold: 0.5
     target_classes:
       - person
       - car
       - bicycle
   ```
3. Place the model weights (`.pt`) in the `models/` directory.
  
To enable face recognition for known-person alerts:
1. Create a `known_faces/` directory at the project root.
2. Add one image per known individual (JPEG/PNG). Filenames (without extensions) are used as labels.
3. In your `on_person_detected` handler, use the FaceRecognizer:
   ```python
   from motion_detector.face_recognizer import FaceRecognizer
   face_recog = FaceRecognizer('known_faces')
   matches = face_recog.recognize(frame)
   for match in matches:
       name = match['name']
       # Include `name` in your notification message
   ```

• Live Feed (port 3000)
  – / renders a simple HTML page (live_feed.html) with an <img> pointing to /video_feed.

• Dashboard & API (port 3001)
  – / now redirects to /dashboard/login.
  – Templates (login.html, dashboard.html) and static (dashboard.css) are loaded from the top-level templates/ and static/ folders.

You can now:

    1. Start the detector:      python -m motion_detector.main
    2. Browse to http://localhost:3000/ to see the live MJPEG stream in your browser.
    3. Browse to http://localhost:3001/ to be redirected to the dashboard login.


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
   - Ensure your firewall allows inbound connections on the port you run the server (default: 3000).
   - For Linux with ufw:
     ```bash
     sudo ufw allow 3000
     ```
3. **Access Remotely:**
   - From any device/browser on your network (or Internet, if port forwarded), visit:
     ```
     http://<your-server-ip>:3000
     ```
4. **Security:**
   - Do NOT share your .env or config.yaml files.
   - For Internet exposure, use authentication, VPN, or firewall rules for safety.

## .gitignore Usage
- A `.gitignore` file is provided to prevent sensitive files from being committed to git.
- By default, `.env`, log files, and other secrets are excluded from version control.

## Remote Access
To access the dashboard and API remotely:
1. Make sure your server firewall allows inbound connections on the relevant port (default: 3000 or 3001).
2. Start the server with:
   ```bash
   python3 motion_detector/main.py
   ```
3. Visit `http://<your-server-ip>:3000` or `http://<your-server-ip>:3001` from your remote device/browser.

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
