import cv2
import numpy as np

class PersonDetector:
    def __init__(self, conf_threshold=0.5):
        # Use MobileNet-SSD pretrained model (prototxt and caffemodel must be present)
        proto = cv2.data.haarcascades + '../../models/MobileNetSSD_deploy.prototxt'
        model = cv2.data.haarcascades + '../../models/MobileNetSSD_deploy.caffemodel'
        self.net = cv2.dnn.readNetFromCaffe(proto, model)
        self.conf_threshold = conf_threshold
        self.class_names = ["background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog",
            "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

    def detect(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        persons = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            idx = int(detections[0, 0, i, 1])
            if confidence > self.conf_threshold and self.class_names[idx] == "person":
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                persons.append((startX, startY, endX, endY, confidence))
        return persons
