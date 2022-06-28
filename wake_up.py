import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

def send_notify(message):
    headers = {
        "Authorization": "Bearer " + os.getenv("LINE_NOTIFY"), 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    payload = {'message': message }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

try:
    response = requests.get(f"{os.getenv('WAKE_UP_URL')}")
    print("喚醒成功")
except json.decoder.JSONDecodeError as e:
    send_notify(f"\喚醒發生錯誤\nErrorMsg:{str(e)}")
    exit()
except Exception as ex:
    send_notify(f"\喚醒發生錯誤\nErrorMsg:{str(ex)}")
    exit()
