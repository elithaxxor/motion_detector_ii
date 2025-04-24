import smtplib
from email.mime.text import MIMEText
import requests
from concurrent.futures import ThreadPoolExecutor
import time
import threading
import os

class Notifier:
    """
    Notification manager for sending alerts via Email, Telegram, WhatsApp, and Discord.
    Features:
      - Asynchronous sending using ThreadPoolExecutor
      - Rate limiting per channel
      - Logging of all notifications (success/failure) with context
      - Simple template support for notification messages
    Args:
        config (dict): Notification configuration dictionary.
        log_file (str): Path to the notification log file (default: 'notification_log.txt').
    """
    def __init__(self, config, log_file="notification_log.txt"):
        """
        Initialize the Notifier with channel configs, logging, and rate limiting.
        """
        self.email_cfg = config.get('email', {})
        self.telegram_cfg = config.get('telegram', {})
        self.whatsapp_cfg = config.get('whatsapp', {})
        self.discord_cfg = config.get('discord', {})
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.log_file = log_file
        self.last_sent = {}  # Tracks last sent time per channel for rate limiting
        self.lock = threading.Lock()  # Protects shared state
        self.rate_limit_seconds = 30  # Minimum seconds between notifications per channel
        # Simple templates, can be expanded
        self.templates = {
            'default': "[{{timestamp}}] {{channel}}: {{subject}} - {{message}}",
        }

    def log_notification(self, channel, subject, message, status, error=None):
        """
        Append a notification event to the log file.
        Args:
            channel (str): Notification channel (email, telegram, etc)
            subject (str): Notification subject
            message (str): Notification message
            status (str): 'SENT' or 'FAILED'
            error (str, optional): Error message if failed
        """
        log_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {channel.upper()} | {subject} | {status} | {message}"
        if error:
            log_entry += f" | ERROR: {error}"
        with self.lock:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")

    def is_rate_limited(self, channel):
        """
        Check if the channel is rate-limited (i.e., recently sent).
        Args:
            channel (str): Notification channel
        Returns:
            bool: True if rate-limited, False otherwise
        """
        now = time.time()
        with self.lock:
            last = self.last_sent.get(channel, 0)
            if now - last < self.rate_limit_seconds:
                return True
            self.last_sent[channel] = now
        return False

    def render_template(self, channel, subject, message):
        """
        Render a notification message using the template for the channel.
        Args:
            channel (str): Channel name
            subject (str): Subject line
            message (str): Main message
        Returns:
            str: Rendered message string
        """
        template = self.templates.get(channel, self.templates['default'])
        return template.replace("{{timestamp}}", time.strftime('%Y-%m-%d %H:%M:%S')) \
            .replace("{{channel}}", channel.upper()) \
            .replace("{{subject}}", subject) \
            .replace("{{message}}", message)

    def send_email(self, subject, body):
        """
        Send an email notification asynchronously if enabled and not rate-limited.
        Logs the result.
        """
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
        """
        Send a Telegram notification if enabled and not rate-limited. Logs the result.
        """
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
        """
        Send a WhatsApp notification if enabled and not rate-limited. Logs the result.
        """
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
        """
        Send a Discord webhook notification if enabled and not rate-limited. Logs the result.
        """
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
        """
        Send notifications to all enabled channels asynchronously using templates.
        """
        rendered = self.render_template('default', subject, message)
        self.executor.submit(self.send_email, subject, rendered)
        self.executor.submit(self.send_telegram, rendered, subject)
        self.executor.submit(self.send_whatsapp, rendered, subject)
        self.executor.submit(self.send_discord, rendered, subject)
