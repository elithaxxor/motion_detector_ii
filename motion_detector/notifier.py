import smtplib
from email.mime.text import MIMEText
import requests
from concurrent.futures import ThreadPoolExecutor
import time
import threading
import os

class Notifier:
    def __init__(self, config, log_file="notification_log.txt"):
        self.email_cfg = config.get('email', {})
        self.telegram_cfg = config.get('telegram', {})
        self.whatsapp_cfg = config.get('whatsapp', {})
        self.discord_cfg = config.get('discord', {})
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.log_file = log_file
        self.last_sent = {}
        self.lock = threading.Lock()
        self.rate_limit_seconds = 30  # Minimum seconds between notifications per channel
        # Simple templates, can be expanded
        self.templates = {
            'default': "[{{timestamp}}] {{channel}}: {{subject}} - {{message}}",
        }

    def log_notification(self, channel, subject, message, status, error=None):
        log_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {channel.upper()} | {subject} | {status} | {message}"
        if error:
            log_entry += f" | ERROR: {error}"
        with self.lock:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")

    def is_rate_limited(self, channel):
        now = time.time()
        with self.lock:
            last = self.last_sent.get(channel, 0)
            if now - last < self.rate_limit_seconds:
                return True
            self.last_sent[channel] = now
        return False

    def render_template(self, channel, subject, message):
        template = self.templates.get(channel, self.templates['default'])
        return template.replace("{{timestamp}}", time.strftime('%Y-%m-%d %H:%M:%S')) \
            .replace("{{channel}}", channel.upper()) \
            .replace("{{subject}}", subject) \
            .replace("{{message}}", message)

    def send_email(self, subject, body):
        channel = 'email'
        if not self.email_cfg.get('enabled', False) or self.is_rate_limited(channel):
            return
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_cfg['from']
        msg['To'] = self.email_cfg['to']
        try:
            with smtplib.SMTP_SSL(self.email_cfg['smtp_server'], self.email_cfg['smtp_port']) as server:
                server.login(self.email_cfg['username'], self.email_cfg['password'])
                server.sendmail(self.email_cfg['from'], [self.email_cfg['to']], msg.as_string())
            self.log_notification(channel, subject, body, 'SENT')
        except smtplib.SMTPException as e:
            self.log_notification(channel, subject, body, 'FAILED', str(e))
        except Exception as e:
            self.log_notification(channel, subject, body, 'FAILED', str(e))

    def send_telegram(self, message, subject="Alert"):
        channel = 'telegram'
        if not self.telegram_cfg.get('enabled', False) or self.is_rate_limited(channel):
            return
        token = self.telegram_cfg['bot_token']
        chat_id = self.telegram_cfg['chat_id']
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {'chat_id': chat_id, 'text': message}
        try:
            requests.post(url, data=data, timeout=5)
            self.log_notification(channel, subject, message, 'SENT')
        except requests.RequestException as e:
            self.log_notification(channel, subject, message, 'FAILED', str(e))
        except Exception as e:
            self.log_notification(channel, subject, message, 'FAILED', str(e))

    def send_whatsapp(self, message, subject="Alert"):
        channel = 'whatsapp'
        if not self.whatsapp_cfg.get('enabled', False) or self.is_rate_limited(channel):
            return
        phone = self.whatsapp_cfg['phone']
        apikey = self.whatsapp_cfg['apikey']
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={apikey}"
        try:
            requests.get(url, timeout=5)
            self.log_notification(channel, subject, message, 'SENT')
        except requests.RequestException as e:
            self.log_notification(channel, subject, message, 'FAILED', str(e))
        except Exception as e:
            self.log_notification(channel, subject, message, 'FAILED', str(e))

    def send_discord(self, message, subject="Alert"):
        channel = 'discord'
        if not self.discord_cfg.get('enabled', False) or self.is_rate_limited(channel):
            return
        webhook_url = self.discord_cfg['webhook_url']
        data = {"content": message}
        try:
            requests.post(webhook_url, json=data, timeout=5)
            self.log_notification(channel, subject, message, 'SENT')
        except requests.RequestException as e:
            self.log_notification(channel, subject, message, 'FAILED', str(e))
        except Exception as e:
            self.log_notification(channel, subject, message, 'FAILED', str(e))

    def notify_all(self, subject, message):
        # Send all notifications asynchronously with template
        rendered = self.render_template('default', subject, message)
        self.executor.submit(self.send_email, subject, rendered)
        self.executor.submit(self.send_telegram, rendered, subject)
        self.executor.submit(self.send_whatsapp, rendered, subject)
        self.executor.submit(self.send_discord, rendered, subject)
