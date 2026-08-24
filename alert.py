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
