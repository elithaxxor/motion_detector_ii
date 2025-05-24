import os
from flask import Flask, jsonify, request, redirect, url_for
from threading import Thread
import time
from dashboard import dashboard_bp

class APIServer(Thread):
    def __init__(self, detector, notifier, live_feed, stop_flag, host='0.0.0.0', port=3001):
        # host, port now configurable via config.yaml
        super().__init__(daemon=True)
        self.detector = detector
        self.notifier = notifier
        self.live_feed = live_feed
        self.stop_flag = stop_flag
        # Configure server host/port and templates
        self.host = host
        self.port = port
        # Use top-level templates and static folders for dashboard
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static'))
        self.app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
        # Session secret key for dashboard login
        self.app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', 'change_this_in_production')
        self.app.register_blueprint(dashboard_bp)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def root():
            return redirect(url_for('dashboard.login'))

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
        self.app.run(host=self.host, port=self.port)
    
    def stop(self):
        """
        Stop the API server. No-op since Flask is running in a daemon thread.
        """
        pass
