import sys
import threading
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
from motion import MotionDetector
from utils import load_config, setup_logger, ensure_log_file

class MotionGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.detector_thread = None
        self.stop_flag = threading.Event()
        self.video_path = None
        self.log_file = None
        self.logger = None
        self.config = None

    def initUI(self):
        self.setWindowTitle('Motion Detector GUI')
        self.setGeometry(100, 100, 400, 300)

        self.status_label = QLabel('Status: Idle')
        self.video_label = QLabel('No video selected')
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.headless_checkbox = QCheckBox('Headless (no video display)')
        self.select_btn = QPushButton('Select Video File')
        self.start_btn = QPushButton('Start Detection')
        self.stop_btn = QPushButton('Stop Detection')
        self.stop_btn.setEnabled(False)

        vbox = QVBoxLayout()
        vbox.addWidget(self.status_label)
        vbox.addWidget(self.video_label)
        vbox.addWidget(self.headless_checkbox)
        vbox.addWidget(self.select_btn)
        vbox.addWidget(self.start_btn)
        vbox.addWidget(self.stop_btn)
        vbox.addWidget(QLabel('Log Output:'))
        vbox.addWidget(self.log_view)
        self.setLayout(vbox)

        self.select_btn.clicked.connect(self.select_video)
        self.start_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)

    def select_video(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Select Video File', os.getcwd(), 'Video Files (*.mp4 *.avi *.mov *.mkv)')
        if fname:
            self.video_path = fname
            self.video_label.setText(f'Video: {os.path.basename(fname)}')
        else:
            self.video_label.setText('No video selected')

    def start_detection(self):
        if self.detector_thread and self.detector_thread.is_alive():
            self.log('Detection already running.')
            return
        self.stop_flag.clear()
        self.status_label.setText('Status: Running')
        self.log('Starting detection...')
        self.config = load_config(os.path.join(os.path.dirname(__file__), 'config.yaml'))
        sensitivity = self.config.get('sensitivity', 800)
        threshold = self.config.get('threshold', 100)
        reference_update = self.config.get('reference_update', True)
        camera_index = self.config.get('camera_index', 0)
        self.log_file = self.config.get('log_file', 'camera_log.txt')
        ensure_log_file(self.log_file)
        self.logger = setup_logger(self.log_file)
        headless = self.headless_checkbox.isChecked()
        self.detector_thread = threading.Thread(target=self.run_detector, args=(sensitivity, threshold, reference_update, camera_index, self.logger, headless))
        self.detector_thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_detection(self):
        self.stop_flag.set()
        self.status_label.setText('Status: Stopping...')
        self.log('Stopping detection...')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def run_detector(self, sensitivity, threshold, reference_update, camera_index, logger, headless):
        detector = MotionDetector(sensitivity, threshold, reference_update, camera_index, logger, video_path=self.video_path)
        try:
            detector.run(None, headless, self.log_file, self.stop_flag)
        except Exception as e:
            self.log(f'[FATAL] {e}')
        self.status_label.setText('Status: Idle')
        self.log('Detection stopped.')

    def log(self, message):
        self.log_view.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MotionGUI()
    gui.show()
    sys.exit(app.exec_())
