# C Motion Detector (OpenCV)

## Features
- Motion detection (frame diff, threshold, contour)
- Configurable via `config.ini` or command-line
- HTTP file upload (libcurl)
- Logging to file
- Hotkeys: `q` (quit), `s` (save snapshot), `r` (reset reference)
- Region of Interest (ROI) support
- Headless mode (no GUI)
- Daemon/service ready (systemd)
- Multi-threaded (capture, processing, upload)
- Multiple camera support (via CLI)
- Hardware acceleration ready (OpenCV CUDA)

## Quick Start

### Build
```
sudo apt install libopencv-dev libcurl4-openssl-dev
make
```

### Run
```
./c_motion_detector            # Camera
./c_motion_detector video.mp4  # Video file
./c_motion_detector --help     # Show options
```

### Systemd Service
See `motion_detector/auto_start.py` for a template to create a systemd service for auto-start.

## Configuration
Edit `config.ini` or use CLI flags. Example:
```
[motion]
min_area = 800
threshold = 25
input = 0
headless = 1
roi = 100,100,400,400

[upload]
url = http://example.com/upload

[log]
file = motion.log
```

## Extending
- Add SFTP/MQTT upload in `upload.c`.
- Add more hotkeys or actions in main loop.
- Add REST API with a C web server (e.g., civetweb, mongoose).
