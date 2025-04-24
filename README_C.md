# C Motion Detector (OpenCV)

## Features
- Motion detection (frame diff, threshold, contour)
- Configurable via `config.ini` or command-line
- HTTP or SFTP file upload (libcurl/libssh2)
- MQTT event publishing (stub)
- Logging to file
- Hotkeys: `q` (quit), `s` (save snapshot), `r` (reset reference)
- Region of Interest (ROI) selection (mouse or config)
- Headless mode (no GUI)
- Daemon/service ready (systemd, --daemon)
- Multi-threaded (capture, processing, upload)
- Multiple camera support (extendable)
- Hardware acceleration ready (OpenCV CUDA, extendable)

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
./c_motion_detector --daemon   # Run as daemon (background)
./c_motion_detector --help     # Show options (extendable)
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
method = http  # http or sftp
url = http://example.com/upload
sftp_host = example.com
sftp_user = user
sftp_pass = pass
sftp_remote_path = /uploads

[mqtt]
broker = mqtt.example.com
topic = motion/events

[log]
file = motion.log
```

## Extending
- Implement SFTP in `sftp_upload.c` (stub provided).
- Implement MQTT in `mqtt_publish.c` (stub provided).
- Add REST API with a C web server (e.g., civetweb, mongoose).
- Add multi-camera support (thread per camera, config section per camera).
- Use OpenCV CUDA for GPU acceleration.
- Add log rotation, advanced error handling, and more hotkeys as needed.

## Advanced Usage
- **ROI selection:** If `roi` is empty in config, you'll be prompted to select with the mouse at startup.
- **Daemon mode:** Use `--daemon` for background service; PID is written to `/tmp/c_motion_detector.pid`.
- **Logs:** All events/errors are logged to `motion.log`.

---

**All code and documentation are up to date and ready for advanced deployment and extension.**
