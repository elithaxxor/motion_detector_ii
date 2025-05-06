import cv2
import imutils
import numpy as np
import time
import logging
import os
from ftp_utils import upload_via_ftp

class MotionDetector:
    def __init__(self, sensitivity, threshold, reference_update, camera_index, logger, video_path=None):
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.reference_update = reference_update
        self.camera_index = camera_index
        self.logger = logger
        self.first_frame = None
        self.avg_frame = None
        self.video_path = video_path

    def process_frame(self, frame):
        greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(greyscale, (21, 21), 0)
        if self.first_frame is None:
            self.first_frame = blurred.copy()
            self.avg_frame = blurred.astype('float')
            return False, frame, None, None
        if self.reference_update:
            cv2.accumulateWeighted(blurred, self.avg_frame, 0.05)
            frame_delta = cv2.absdiff(blurred, cv2.convertScaleAbs(self.avg_frame))
        else:
            frame_delta = cv2.absdiff(self.first_frame, blurred)
        thresh = cv2.threshold(frame_delta, self.threshold, 255, cv2.THRESH_BINARY)[1]
        dilated = cv2.dilate(thresh, None, iterations=2)
        cnts, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected = False
        for c in cnts:
            if cv2.contourArea(c) > self.sensitivity:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                detected = True
        return detected, frame, dilated, frame_delta

    def run(self, hotkey, headless, log_file, stop_flag):
        try:
            # Use video file if provided, else use camera
            if self.video_path:
                self.logger.info(f"Attempting to open video file: {self.video_path}")
                cap = cv2.VideoCapture(self.video_path)
                if not cap.isOpened():
                    self.logger.error(f"Unable to open video file: {self.video_path}")
                    print(f"[ERROR] Unable to open video file: {self.video_path}")
                    return
            else:
                self.logger.info(f"Attempting to open camera (index: {self.camera_index})")
                cap = cv2.VideoCapture(self.camera_index)
                if not cap.isOpened():
                    self.logger.error(f"Unable to open camera (index: {self.camera_index})")
                    print(f"[ERROR] Unable to open camera (index: {self.camera_index})")
                    return
            time.sleep(2)
            self.logger.info("Video stream started.")
            while not stop_flag.is_set():
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning("End of video stream or cannot read frame.")
                    print("[INFO] End of video stream or cannot read frame.")
                    break
                frame = imutils.resize(frame, width=500)
                detected, out_frame, dilated, frame_delta = self.process_frame(frame)
                status = 'Detected' if detected else 'Undetected'
                if detected:
                    msg = f'[Detected] {time.ctime()}'
                    self.logger.info(msg)
                    with open(log_file, 'a') as f:
                        f.write(msg + '\n')
                if not headless:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(out_frame, f'Room Status: {status}', (10, 20), font, 0.5, (0, 0, 255), 2)
                    cv2.putText(out_frame, f'Time: {time.ctime()}', (10, out_frame.shape[0] - 10), font, 0.35, (0, 0, 255), 1)
                    cv2.imshow('[Security Feed]', out_frame)
                    if dilated is not None:
                        cv2.imshow('Threshold [Front-Image]', dilated)
                    if frame_delta is not None:
                        cv2.imshow('Frame_Delta', frame_delta)
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC for emergency exit
                        self.logger.info('ESC pressed, exiting.')
                        break
                # After detection logic, when saving a frame (example):
                # cv2.imwrite(save_path, frame)
                # upload_via_ftp(save_path)
            cap.release()
            cv2.destroyAllWindows()
            self.logger.info("Video stream ended and resources released.")
        except Exception as e:
            self.logger.exception(f"Fatal error in run(): {e}")
            print(f"[FATAL] {e}")
