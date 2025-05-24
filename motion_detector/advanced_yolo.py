import os
import numpy as np
try:
    from ultralytics import YOLO
except ImportError:
    raise ImportError("ultralytics must be installed for AdvancedYOLODetector. Please install via 'pip install ultralytics'.")

class AdvancedYOLODetector:
    """
    Advanced YOLOv5/v8 detector supporting multi-class detection.

    Args:
        model_path (str): Path to the YOLO model weights file (e.g., 'yolov5s.pt').
        conf_threshold (float): Confidence threshold for detections.
        target_classes (list): List of class names to filter (e.g., ['person','car']).
        device (str or None): PyTorch device (e.g., 'cpu' or 'cuda:0').
    """
    def __init__(self, model_path='yolov5s.pt', conf_threshold=0.5, target_classes=None, device=None):
        self.model = YOLO(model_path)
        if device:
            self.model.to(device)
        self.conf_threshold = conf_threshold
        # Load class names from model
        self.class_names = self.model.names
        # If no target_classes specified, detect all classes
        if target_classes is None:
            self.target_classes = list(self.class_names.values()) if isinstance(self.class_names, dict) else self.class_names
        else:
            self.target_classes = target_classes

    def detect(self, frame):
        """
        Run inference on a single frame and return filtered detections.

        Returns:
            List of tuples: (x1, y1, x2, y2, confidence, class_name)
        """
        # Inference (returns a list of Results, one per image)
        results = self.model(frame)[0]
        # Extract boxes, confidences, and class IDs
        xyxy = results.boxes.xyxy.cpu().numpy()  # shape (N,4)
        confidences = results.boxes.conf.cpu().numpy()  # shape (N,)
        class_ids = results.boxes.cls.cpu().numpy().astype(int)  # shape (N,)
        detections = []
        for idx, (box, conf, cid) in enumerate(zip(xyxy, confidences, class_ids)):
            if conf < self.conf_threshold:
                continue
            # Decode class name
            name = self.class_names[cid] if cid < len(self.class_names) else str(cid)
            if name not in self.target_classes:
                continue
            x1, y1, x2, y2 = box.astype(int)
            detections.append((x1, y1, x2, y2, float(conf), name))
        return detections
    
# End of file