from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify
from functools import wraps
import yaml
import os
import psutil

# Simple password for demonstration (should be hashed in production)
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "admin")

dashboard_bp = Blueprint('dashboard', __name__)

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

@dashboard_bp.route('/health')
def health():
    # Camera status: check if camera is available (simulate for now)
    camera_status = True
    # Notification channel config status
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
    notif_status = {}
    for ch in ['email', 'telegram', 'whatsapp', 'discord']:
        notif_status[ch] = bool(config.get(ch, {}).get('enabled', False))
    # Disk space
    disk = psutil.disk_usage('/')
    disk_ok = disk.percent < 90
    return jsonify({
        'camera': camera_status,
        'notifications': notif_status,
        'disk_ok': disk_ok,
        'disk_percent': disk.percent
    })
