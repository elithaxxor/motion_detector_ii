import smtplib
from email.mime.text import MIMEText
import requests
from concurrent.futures import ThreadPoolExecutor

class Notifier:
    def __init__(self, config):
        self.email_cfg = config.get('email', {})
        self.telegram_cfg = config.get('telegram', {})
        self.whatsapp_cfg = config.get('whatsapp', {})
        self.discord_cfg = config.get('discord', {})
        self.executor = ThreadPoolExecutor(max_workers=4)

    def send_email(self, subject, body):
        if not self.email_cfg.get('enabled', False):
            return
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_cfg['from']
        msg['To'] = self.email_cfg['to']
        try:
            with smtplib.SMTP_SSL(self.email_cfg['smtp_server'], self.email_cfg['smtp_port']) as server:
                server.login(self.email_cfg['username'], self.email_cfg['password'])
                server.sendmail(self.email_cfg['from'], [self.email_cfg['to']], msg.as_string())
        except smtplib.SMTPException as e:
            print(f"Email notification error: {e}")
        except Exception as e:
            print(f"Unexpected email error: {e}")

    def send_telegram(self, message):
        if not self.telegram_cfg.get('enabled', False):
            return
        token = self.telegram_cfg['bot_token']
        chat_id = self.telegram_cfg['chat_id']
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {'chat_id': chat_id, 'text': message}
        try:
            requests.post(url, data=data, timeout=5)
        except requests.RequestException as e:
            print(f"Telegram notification error: {e}")
        except Exception as e:
            print(f"Unexpected telegram error: {e}")

    def send_whatsapp(self, message):
        if not self.whatsapp_cfg.get('enabled', False):
            return
        # Using CallMeBot (https://www.callmebot.com/) for WhatsApp API
        phone = self.whatsapp_cfg['phone']
        apikey = self.whatsapp_cfg['apikey']
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={apikey}"
        try:
            requests.get(url, timeout=5)
        except requests.RequestException as e:
            print(f"WhatsApp notification error: {e}")
        except Exception as e:
            print(f"Unexpected WhatsApp error: {e}")

    def send_discord(self, message):
        if not self.discord_cfg.get('enabled', False):
            return
        webhook_url = self.discord_cfg['webhook_url']
        data = {"content": message}
        try:
            requests.post(webhook_url, json=data, timeout=5)
        except requests.RequestException as e:
            print(f"Discord notification error: {e}")
        except Exception as e:
            print(f"Unexpected Discord error: {e}")

    def notify_all(self, subject, message):
        # Send all notifications asynchronously
        self.executor.submit(self.send_email, subject, message)
        self.executor.submit(self.send_telegram, message)
        self.executor.submit(self.send_whatsapp, message)
        self.executor.submit(self.send_discord, message)
