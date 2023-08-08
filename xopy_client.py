import pyperclip
import time
import threading
import datetime
import firebase_admin
from firebase_admin import credentials, db

class ClipboardMonitor:
    def __init__(self, credential_path, firebase_url):
        self.recent_value = pyperclip.paste()
        self.is_monitoring = False
        cred = credentials.Certificate(credential_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': firebase_url
        })

    def start(self):
        self.is_monitoring = True
        self.thread = threading.Thread(target=self._monitor_clipboard)
        self.thread.start()

    def stop(self):
        self.is_monitoring = False
        self.thread.join()

    def _monitor_clipboard(self):
        while self.is_monitoring:
            tmp_value = pyperclip.paste()
            if tmp_value != self.recent_value:
                self.recent_value = tmp_value
                timestamp = datetime.datetime.now().isoformat()  # get the current time
                db.reference('clipboard').push({'text': self.recent_value, 'timestamp': timestamp})  # push a new node to the 'clipboard' reference in the Firebase database
                print("Clipboard value changed to: " + self.recent_value)
            time.sleep(0.1)  # pause for a short period to prevent high CPU utilization

# Example usage
key = "/Users/kun/codes/Xopy/xopy-1f467-firebase-adminsdk-hrzkn-c9b4778f49.json"
monitor = ClipboardMonitor(key, 'https://xopy-1f467-default-rtdb.firebaseio.com/')
monitor.start()

# when you want to stop monitoring
# monitor.stop()