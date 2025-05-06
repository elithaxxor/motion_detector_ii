import threading
import time
import psutil
import json
import os

class ResourceMonitor:
    """
    Monitors system resources (disk, CPU, memory) and notifies if thresholds are exceeded.
    Thresholds can be updated at runtime by changing the resource_thresholds.json file.
    """
    def __init__(self, notifier, check_interval=30, thresholds_file=None):
        """
        Args:
            notifier (Notifier): Instance of Notifier to send alerts.
            check_interval (int): Seconds between checks.
            thresholds_file (str): Path to thresholds JSON file.
        """
        self.notifier = notifier
        self.check_interval = check_interval
        self.thresholds_file = thresholds_file or os.path.abspath(os.path.join(os.path.dirname(__file__), '../resource_thresholds.json'))
        self.last_alert = {}  # Avoid spamming alerts
        self.status = {'disk': 0, 'cpu': 0, 'memory': 0}
        self.running = False
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self._load_thresholds()

    def _load_thresholds(self):
        try:
            with open(self.thresholds_file, 'r') as f:
                self.thresholds = json.load(f)
        except Exception:
            self.thresholds = {'disk': 90, 'cpu': 90, 'memory': 90}

    def update_thresholds(self, new_thresholds):
        self.thresholds = new_thresholds
        with open(self.thresholds_file, 'w') as f:
            json.dump(self.thresholds, f)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def _monitor(self):
        while self.running:
            self._load_thresholds()  # Reload thresholds every cycle
            disk = psutil.disk_usage('/')
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            self.status = {
                'disk': disk.percent,
                'cpu': cpu,
                'memory': memory
            }
            now = time.time()
            # Check thresholds and alert if needed
            for resource, percent in self.status.items():
                threshold = self.thresholds.get(resource, 90)
                if percent >= threshold:
                    # Only alert once every 10 minutes per resource
                    last = self.last_alert.get(resource, 0)
                    if now - last > 600:
                        msg = f"Resource Alert: {resource.upper()} usage at {percent:.1f}% (threshold {threshold}%)"
                        self.notifier.notify_all(f"{resource.upper()} ALERT", msg)
                        self.last_alert[resource] = now
            time.sleep(self.check_interval)

    def get_status(self):
        """Return the latest resource status."""
        return self.status.copy()

    def get_thresholds(self):
        """Return current thresholds."""
        return self.thresholds.copy()
