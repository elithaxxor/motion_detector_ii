import threading
import cv2
from flask import Flask, Response

class LiveFeedManager:
    def __init__(self):
        self.active = False
        self.frame = None
        self.lock = threading.Lock()
        self.thread = None
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/video_feed')
        def video_feed():
            return Response(self._gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def _gen(self):
        while self.active:
            with self.lock:
                if self.frame is not None:
                    ret, jpeg = cv2.imencode('.jpg', self.frame)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            cv2.waitKey(1)

    def start(self, host='0.0.0.0', port=5000):
        if self.thread is None or not self.thread.is_alive():
            self.active = True
            self.thread = threading.Thread(target=self.app.run, kwargs={'host': host, 'port': port, 'threaded': True}, daemon=True)
            self.thread.start()

    def stop(self):
        self.active = False

    def update_frame(self, frame):
        with self.lock:
            self.frame = frame.copy()

    def is_running(self):
        return self.active and self.thread and self.thread.is_alive()
