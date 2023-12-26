import requests
import json

with open("auth.json", "r") as f:
    auth_ip = json.load(f)

DEVICE_IP = auth_ip["ip"]
nanoleaf_ip = DEVICE_IP

url = f"http://{nanoleaf_ip}:16021/api/v1/new"

try:
    response = requests.post(url)
    if response.status_code == 200:
        auth_token = response.json()['auth_token']
        print(f"Authorization token: {auth_token}")
    else:
        print("Failed to get authorization token. Make sure you're in pairing mode.")
except Exception as e:
    print(f"Error: {e}")
