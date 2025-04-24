from flask import Flask, jsonify, request
from threading import Thread
import time

class APIServer(Thread):
    def __init__(self, detector, notifier, live_feed, stop_flag):
        super().__init__(daemon=True)
        self.detector = detector
        self.notifier = notifier
        self.live_feed = live_feed
        self.stop_flag = stop_flag
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/status')
        def status():
            return jsonify({
                'live_feed': self.live_feed.is_running(),
                'detection_active': not self.stop_flag.is_set()
            })

        @self.app.route('/notify', methods=['POST'])
        def notify():
            data = request.get_json()
            subject = data.get('subject', 'Alert')
            body = data.get('body', '')
            self.notifier.notify_all(subject, body)
            return jsonify({'status': 'sent'})

        @self.app.route('/control', methods=['POST'])
        def control():
            data = request.get_json()
            action = data.get('action')
            if action == 'stop':
                self.stop_flag.set()
                return jsonify({'status': 'stopped'})
            elif action == 'start':
                if self.stop_flag.is_set():
                    self.stop_flag.clear()
                return jsonify({'status': 'started'})
            return jsonify({'status': 'unknown action'})

    def run(self):
        self.app.run(host='0.0.0.0', port=8000)
