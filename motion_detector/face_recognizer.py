import os
try:
    import face_recognition
except ImportError:
    raise ImportError("face_recognition must be installed for FaceRecognizer. Please install via 'pip install face_recognition'.")

class FaceRecognizer:
    """
    Face recognizer for known-person alerts using face_recognition library.

    Args:
        known_faces_dir (str): Directory containing images of known persons. File names (without extension) are used as labels.
        tolerance (float): Distance tolerance for face matching (default 0.6).
    """
    def __init__(self, known_faces_dir, tolerance=0.6):
        self.known_encodings = []
        self.known_names = []
        self.tolerance = tolerance
        # Load known faces
        for fname in os.listdir(known_faces_dir):
            path = os.path.join(known_faces_dir, fname)
            name, ext = os.path.splitext(fname)
            if ext.lower() not in ('.jpg', '.jpeg', '.png'):
                continue
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                self.known_encodings.append(encodings[0])
                self.known_names.append(name)

    def recognize(self, frame):
        """
        Recognize known faces in a frame.

        Args:
            frame (ndarray): BGR image (numpy array).
        Returns:
            List of dicts: [{'name': str, 'box': (left, top, right, bottom)}]
        """
        # Convert BGR to RGB
        rgb = frame[:, :, ::-1]
        # Detect faces and compute encodings
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)
        results = []
        for loc, enc in zip(locations, encodings):
            # Compare to known encodings
            matches = face_recognition.compare_faces(self.known_encodings, enc, self.tolerance)
            name = 'Unknown'
            if matches and any(matches):
                # Select best match
                distances = face_recognition.face_distance(self.known_encodings, enc)
                best_idx = distances.argmin()
                if matches[best_idx]:
                    name = self.known_names[best_idx]
            top, right, bottom, left = loc
            results.append({'name': name, 'box': (left, top, right, bottom)})
        return results

# End of file