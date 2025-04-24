import unittest
from motion_detector.notifier import Notifier

class DummyConfig:
    def get(self, key, default=None):
        return default

class TestNotifier(unittest.TestCase):
    def setUp(self):
        self.notifier = Notifier({
            'email': {'enabled': False},
            'telegram': {'enabled': False},
            'whatsapp': {'enabled': False},
            'discord': {'enabled': False},
        })

    def test_send_email_disabled(self):
        # Should not raise or send
        self.notifier.send_email('Test', 'Body')

    def test_send_telegram_disabled(self):
        self.notifier.send_telegram('Test')

    def test_send_whatsapp_disabled(self):
        self.notifier.send_whatsapp('Test')

    def test_send_discord_disabled(self):
        self.notifier.send_discord('Test')

if __name__ == '__main__':
    unittest.main()
