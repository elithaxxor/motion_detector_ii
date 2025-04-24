import threading
from pynput import keyboard

class HotkeyListener:
    def __init__(self, hotkey_sequence, stop_flag):
        self.hotkey_sequence = hotkey_sequence
        self.stop_flag = stop_flag
        self.listener = None

    def on_activate(self):
        print(f"Hotkey '{self.hotkey_sequence}' detected. Stopping motion detector.")
        self.stop_flag.set()

    def start(self):
        # Parse hotkey string (e.g., 'ctrl+l')
        keys = self.hotkey_sequence.lower().split('+')
        modifiers = set()
        key_char = None
        for k in keys:
            if k == 'ctrl':
                modifiers.add(keyboard.Key.ctrl_l)
            elif k == 'alt':
                modifiers.add(keyboard.Key.alt_l)
            elif k == 'shift':
                modifiers.add(keyboard.Key.shift)
            else:
                key_char = k
        current = set()
        def on_press(key):
            if key in modifiers:
                current.add(key)
            if hasattr(key, 'char') and key.char == key_char:
                if all(m in current for m in modifiers):
                    self.on_activate()
        def on_release(key):
            if key in current:
                current.remove(key)
        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
