# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Initial CHANGELOG.md created.
- Dashboard with live detection, resource, and notification logs.
- Multi-channel notification support (Email, Telegram, WhatsApp, Discord).
- REST API for status, notification, and control.
- Hotkey support for quick system control.
- Modular codebase for extensibility (multi-camera, cloud upload, face/object recognition).
- Security recommendations for config and model files.
- .env file for secure API key management (Telegram, WhatsApp, Discord, Shodan)
- Shodan API integration (search and host lookup utilities)
- Multi-channel notifications: person detection alerts sent to Telegram, WhatsApp, Discord
- Remote access support: listen on 0.0.0.0 for web server and API

### Changed
- Improved README documentation and structure.
- Moved C code to YOLO_EMBEDDED directory
- Updated requirements.txt (added python-dotenv, shodan)

### Fixed
- General bug fixes and stability improvements.
- Improved notification logic for per-camera config

---

## [2025-05-06]
### Updated
- README.md reviewed and improved for clarity and completeness
- Added troubleshooting section for OpenCV and common installation issues
- Clarified C++ and Python integration instructions
- Refined YOLO_EMBEDDED section for embedded/edge use

---

## [2025-05-05] (maintenance)
### Added
- YOLO_EMBEDDED section in README.md with installation and usage instructions
- Comprehensive .gitignore for Python, C++, IDEs, logs, model files, and more
- Clarified installation requirements (OpenCV, numpy, Flask, etc.)

### Changed
- README.md updated for clarity, new user onboarding, and YOLO_EMBEDDED documentation
- .gitignore extended for C++/YOLO/IDE/OS artifacts

### Fixed
- Documented missing dependencies for running tests (cv2)
- Minor README formatting and structure improvements

---

## [2025-05-05]
### Added
- Instructions for remote access: how to access the dashboard/API from any device using your server's IP address and firewall settings.
- .gitignore file to exclude .env, logs, and sensitive files from version control.

### Changed
- Expanded README with step-by-step instructions for remote access and securing sensitive information.

---

## [2025-04-28] (current release)
### Added
- YOLOv3-tiny person detection integration.
- On-demand live feed (GUI and web) triggered by detection.
- Notification system with snapshot support.
- Resource and health monitoring on dashboard.
- File structure documentation in README.
