import requests
import json
import sys
from getnanoIDs import get_panel_ids

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    hlen = len(hex_color)
    return tuple(int(hex_color[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

# Function to create effect data for a single panel with transition time
def create_single_panel_effect_data(panel_id, rgb_color, transition_time=50):
    panel_data = f"1 {panel_id} 1 {rgb_color[0]} {rgb_color[1]} {rgb_color[2]} 0 0 {transition_time}"
    return panel_data

# Function to send effect data for a single panel
def send_effect_data(effect_data):
    effect_json = {
        "command": "display",
        "animType": "static",
        "animData": effect_data,
        "loop": False,
        "palette": []
    }

    url = f"http://{DEVICE_IP}:16021/api/v1/{AUTH_TOKEN}/effects"
    headers = {'Content-Type': 'application/json'}

    response = requests.put(url, data=json.dumps({"write": effect_json}), headers=headers)
    if response.status_code not in [200, 204]:
        print(f"HTTP Error: Status code {response.status_code}")
        print(f"Response: {response.text}")

# Function to set all panels to a single color
def set_all_panels_to_color(hex_color, panel_ids, transition_time=100):
    rgb_color = hex_to_rgb(hex_color)
    for panel_id in panel_ids:
        effect_data = create_single_panel_effect_data(panel_id, rgb_color, transition_time)
        send_effect_data(effect_data)

with open("auth.json", "r") as f:
    auth_ip = json.load(f)

DEVICE_IP = auth_ip["ip"]
AUTH_TOKEN = auth_ip["auth"]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        hex_color = "#FFFFFF"
        print("Usage: py set_hex.py #HEXCOLOR")
        # sys.exit(1)
    else:
        hex_color = sys.argv[1]  # Get hex color from command line argument
    
    try:
        with open("panelIDs.json", "r") as f:
            panel_ids = json.load(f)["ids"]
        if len(panel_ids) == 0:
            raise FileNotFoundError
    except FileNotFoundError:
        panel_ids = get_panel_ids()
        if len(panel_ids) > 0:
            with open("panelIDs.json", "x") as f:
                json.dump(obj={"ids": panel_ids}, fp=f)


    # panel_ids = [57011, 35422, 33728]  # Replace with your actual panel IDs

    set_all_panels_to_color(hex_color, panel_ids, transition_time=50)  # Adjust the transition time as needed
