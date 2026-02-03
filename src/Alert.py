import requests
from dotenv import load_dotenv
import os

load_dotenv()

ALERT_URL = os.getenv("ALERT_URL")
ALERT_PORT = os.getenv("ALERT_PORT")

def send_alert(message):
    url = f"{ALERT_URL}:{ALERT_PORT}/notify"
    payload = {"message": message}

    try:
        requests.post(url, json=payload, timeout=2)
    except Exception as e:
        print(f"Failed to send alert: {e}")