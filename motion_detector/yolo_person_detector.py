import cv2
import numpy as np
import os

class YoloPersonDetector:
    def __init__(self, model_dir=None, conf_threshold=0.5, nms_threshold=0.3):
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), '../models')
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.classes = []
        with open(os.path.join(model_dir, 'coco.names'), 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.net = cv2.dnn.readNet(os.path.join(model_dir, 'yolov3-tiny.weights'),
                                   os.path.join(model_dir, 'yolov3-tiny.cfg'))
        self.person_class_id = self.classes.index('person')

    def detect(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        ln = self.net.getUnconnectedOutLayersNames()
        layerOutputs = self.net.forward(ln)
        boxes, confidences = [], []
        h, w = frame.shape[:2]
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if classID == self.person_class_id and confidence > self.conf_threshold:
                    box = detection[0:4] * np.array([w, h, w, h])
                    (centerX, centerY, width, height) = box.astype('int')
                    x = int(centerX - width / 2)
                    y = int(centerY - height / 2)
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        results = []
        if len(idxs) > 0:
            for i in idxs.flatten():
                x, y, w, h = boxes[i]
                conf = confidences[i]
                results.append((x, y, x + w, y + h, conf))
        return results
