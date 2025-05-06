from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify
from functools import wraps
import yaml
import os
import psutil
from motion_detector.resource_monitor import ResourceMonitor

# Simple password for demonstration (should be hashed in production)
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "admin")

dashboard_bp = Blueprint('dashboard', __name__)

# Global resource monitor instance (set in main)
resource_monitor = None

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('dashboard.login'))
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route('/dashboard/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == DASHBOARD_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard.status'))
        else:
            error = 'Invalid password.'
    return render_template('login.html', error=error)

@dashboard_bp.route('/dashboard/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('dashboard.login'))

@dashboard_bp.route('/dashboard/status')
@login_required
def status():
    # Load detection log (last 20 events)
    log_path = os.path.join(os.path.dirname(__file__), '../camera_log.txt')
    detections = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            detections = f.readlines()[-20:]
    # Load notification log (last 20 events)
    notif_log_path = os.path.join(os.path.dirname(__file__), '../notification_log.txt')
    notifications = []
    if os.path.exists(notif_log_path):
        with open(notif_log_path) as f:
            notifications = f.readlines()[-20:]
    # Load notification config
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    channels = {
        'email': config.get('email', {}).get('enabled', False),
        'telegram': config.get('telegram', {}).get('enabled', False),
        'whatsapp': config.get('whatsapp', {}).get('enabled', False),
        'discord': config.get('discord', {}).get('enabled', False),
    }
    return render_template('dashboard.html', detections=detections, notifications=notifications, channels=channels)

@dashboard_bp.route('/dashboard/log/<logtype>')
@login_required
def download_log(logtype):
    if logtype == 'notification':
        path = os.path.join(os.path.dirname(__file__), '../notification_log.txt')
    else:
        path = os.path.join(os.path.dirname(__file__), '../camera_log.txt')
    if not os.path.exists(path):
        return 'Log not found', 404
    return send_file(path, as_attachment=True)

@dashboard_bp.route('/dashboard/logs_ajax')
@login_required
def logs_ajax():
    notif_log_path = os.path.join(os.path.dirname(__file__), '../notification_log.txt')
    detection_log_path = os.path.join(os.path.dirname(__file__), '../camera_log.txt')
    notifications = []
    detections = []
    # Get filter params
    notif_filter = request.args.get('notif_filter', '').strip().lower()
    notif_channel = request.args.get('notif_channel', '').strip().lower()
    notif_status = request.args.get('notif_status', '').strip().lower()
    detect_filter = request.args.get('detect_filter', '').strip().lower()
    if os.path.exists(notif_log_path):
        with open(notif_log_path) as f:
            logs = f.readlines()[-100:]
            filtered = []
            for l in logs:
                l_low = l.lower()
                if notif_filter and notif_filter not in l_low:
                    continue
                if notif_channel and f"{notif_channel.upper()} |" not in l:
                    continue
                if notif_status and notif_status.upper() not in l:
                    continue
                filtered.append(l)
            notifications = filtered[-20:]
    if os.path.exists(detection_log_path):
        with open(detection_log_path) as f:
            logs = f.readlines()[-100:]
            detections = [l for l in logs if detect_filter in l.lower()][-20:]
    return jsonify({'notifications': notifications, 'detections': detections})

@dashboard_bp.route('/dashboard/clear_log/<logtype>', methods=['POST'])
@login_required
def clear_log(logtype):
    if logtype == 'notification':
        path = os.path.join(os.path.dirname(__file__), '../notification_log.txt')
    else:
        path = os.path.join(os.path.dirname(__file__), '../camera_log.txt')
    open(path, 'w').close()
    return '', 204

@dashboard_bp.route('/dashboard/resource_thresholds', methods=['GET', 'POST'])
@login_required
def resource_thresholds():
    global resource_monitor
    if request.method == 'POST':
        data = request.json
        # Validate input
        try:
            disk = int(data.get('disk', 90))
            cpu = int(data.get('cpu', 90))
            memory = int(data.get('memory', 90))
            new_thresholds = {'disk': disk, 'cpu': cpu, 'memory': memory}
            resource_monitor.update_thresholds(new_thresholds)
            return jsonify({'ok': True, 'thresholds': new_thresholds})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 400
    else:
        thresholds = resource_monitor.get_thresholds() if resource_monitor else {'disk': 90, 'cpu': 90, 'memory': 90}
        return jsonify(thresholds)

# --- FTP Config Routes ---
from flask import current_app
import json

@dashboard_bp.route('/dashboard/ftp_config', methods=['GET', 'POST'])
@login_required
def ftp_config():
    config_path = os.path.join(os.path.dirname(__file__), '../ftp_config.json')
    if request.method == 'POST':
        data = request.json
        with open(config_path, 'w') as f:
            json.dump(data, f)
        return jsonify({'ok': True})
    else:
        if os.path.exists(config_path):
            with open(config_path) as f:
                data = json.load(f)
        else:
            data = {}
        return jsonify(data)

@dashboard_bp.route('/dashboard/ftp_test', methods=['POST'])
@login_required
def ftp_test():
    from ftp_utils import upload_via_ftp
    import tempfile
    try:
        # Create a temp file and attempt upload
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            f.write('FTP test file')
            temp_path = f.name
        upload_via_ftp(temp_path, 'ftp_test_file.txt')
        os.remove(temp_path)
        return jsonify({'ok': True, 'msg': 'FTP upload succeeded.'})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})

@dashboard_bp.route('/dashboard/ftp_upload_log')
@login_required
def ftp_upload_log():
    log_path = os.path.join(os.path.dirname(__file__), '../ftp_upload.log')
    if not os.path.exists(log_path):
        return jsonify([])
    with open(log_path, 'r') as f:
        lines = f.readlines()
    # Return last 20 entries, newest last
    return jsonify([l.strip() for l in lines[-20:]])

@dashboard_bp.route('/health')
def health():
    # Camera status: check if camera is available (simulate for now)
    camera_status = True
    # Notification channel config status
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    notif_status = {ch: bool(config.get(ch, {}).get('enabled', False)) for ch in ['email', 'telegram', 'whatsapp', 'discord']}
    # Disk space
    disk = psutil.disk_usage('/')
    disk_ok = disk.percent < 90
    # Resource monitor status
    res_status = resource_monitor.get_status() if resource_monitor else {}
    return jsonify({
        'camera': camera_status,
        'notifications': notif_status,
        'disk_ok': disk_ok,
        'disk_percent': disk.percent,
        'resource_status': res_status
    })
