import pyperclip
import time
import threading
import datetime
import firebase_admin
from firebase_admin import credentials, db
from pyperclip import PyperclipException


class ClipboardMonitor:
    def __init__(self, credential_path, firebase_url):
        self.recent_value = pyperclip.paste()
        self.is_monitoring = False
        cred = credentials.Certificate(credential_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': firebase_url
        })
        self.clipboard_ref = db.reference('clipboard')
        self.clipboard_ref.listen(self.on_clipboard_update)

    def start(self):
        self.is_monitoring = True
        self.thread = threading.Thread(target=self._monitor_clipboard)
        self.thread.start()

    def stop(self):
        self.is_monitoring = False
        self.thread.join()

    def on_clipboard_update(self, event):
        clipboard_data = self.clipboard_ref.get()
        latest_timestamp = max(clipboard_data.keys())
        latest_clipboard_text = clipboard_data[latest_timestamp]
        if latest_clipboard_text != self.recent_value and \
                isinstance(latest_clipboard_text, (str, int, float, bool)):
            self.recent_value = latest_clipboard_text
            pyperclip.copy(self.recent_value)  # update the local clipboard
            print("Clipboard value changed to: " + pyperclip.paste())

    def _monitor_clipboard(self):
        while self.is_monitoring:
            try:
                tmp_value = pyperclip.paste()
            except PyperclipException as e:
                print(f"Failed to paste from clipboard: {e}")
                continue

            if tmp_value != self.recent_value:
                self.recent_value = tmp_value
                timestamp = datetime.datetime.now().isoformat()  # get the current time
                # push a new node to the 'clipboard' reference in the Firebase database
                try:
                    db.reference('clipboard').push(
                        {'text': self.recent_value, 'timestamp': timestamp})
                except Exception as e:
                    print(f"Failed to push to Firebase: {e}")
                    continue

                print("Clipboard value changed to: " + self.recent_value)
            # pause for a short period to prevent high CPU utilization
            time.sleep(0.01)


# Example usage
key = "/Users/kun/codes/Xopy/xopy-1f467-firebase-adminsdk-hrzkn-c9b4778f49.json"
monitor = ClipboardMonitor(
    key, 'https://xopy-1f467-default-rtdb.firebaseio.com/')
monitor.start()
