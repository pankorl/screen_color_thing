from nanoleafapi import Nanoleaf
import sys
import json
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
auth_file_path = os.path.join(script_dir, 'auth.json')
with open(auth_file_path, "r") as f:
    auth_ip = json.load(f)

DEVICE_IP = auth_ip["ip"]
AUTH_TOKEN = auth_ip["auth"]

nl = Nanoleaf(DEVICE_IP, AUTH_TOKEN)

def print_panel_ids():
    try:
        layout = nl.get_layout()
        print("Panel IDs and their positions:")
        for panel in layout['positionData']:
            print(f"ID: {panel['panelId']}, x: {panel['x']}, y: {panel['y']}")
    except Exception as e:
        print(f"Error: {e}")

def get_panel_ids():
    panelids = []
    try:
        layout = nl.get_layout()
        # print("Panel IDs and their positions:")
        for panel in layout['positionData']:
            if panel['panelId'] != 0:
                panelids.append(panel['panelId'])
            # print(f"ID: {panel['panelId']}, x: {panel['x']}, y: {panel['y']}")
        return panelids
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print_panel_ids()
