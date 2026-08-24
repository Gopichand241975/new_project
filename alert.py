"""alerts.py — Telegram alert sending + camera tamper detection."""

import time
import cv2
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TAMPER_BLACKOUT_THRESHOLD = 15
TAMPER_DURATION_SECONDS = 3

def send_alert(message, snapshot_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=5)
        if snapshot_path:
            photo_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            with open(snapshot_path, "rb") as photo:
                requests.post(photo_url, data={"chat_id": TELEGRAM_CHAT_ID},
                               files={"photo": photo}, timeout=10)
    except requests.RequestException as e:
        print(f"[ALERT ERROR] Failed to send Telegram alert: {e}")


class TamperMonitor:
    def __init__(self):
        self._dark_since = None
        self._alerted = False

    def check(self, frame, camera_name="Camera"):
        mean_intensity = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean()
        now = time.time()
        if mean_intensity < TAMPER_BLACKOUT_THRESHOLD:
            self._dark_since = self._dark_since or now
            if (now - self._dark_since) >= TAMPER_DURATION_SECONDS and not self._alerted:
                send_alert(f"Tamper alert: {camera_name} feed appears blocked or disconnected.")
                self._alerted = True
        else:
            self._dark_since = None
            self._alerted = False
