from flask import Blueprint, render_template, request, redirect, url_for, session
from functools import wraps
import yaml
import os

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
