import requests
import json

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    hlen = len(hex_color)
    return tuple(int(hex_color[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

# Function to create effect data for a single panel with transition time
def create_single_panel_effect_data(panel_id, rgb_color, transition_time=50):
    # Panel data string for one panel with transition time for fade effect
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

# Function to set individual panel colors with fade
def set_individual_panel_colors(panel_colors, transition_time=100):
    for panel_id, hex_color in panel_colors.items():
        rgb_color = hex_to_rgb(hex_color)
        effect_data = create_single_panel_effect_data(panel_id, rgb_color, transition_time)
        send_effect_data(effect_data)

with open("auth.json", "r") as f:
    auth_ip = json.load(f)

DEVICE_IP = auth_ip["ip"]
AUTH_TOKEN = auth_ip["auth"]

if __name__ == "__main__":
    panel_colors = {
        57011: '#FF0000',  # Red color for panel ID 1
        35422: '#00FFFF',  # Cyan color for panel ID 2
        # Add more panels and colors as needed
    }

    set_individual_panel_colors(panel_colors, transition_time=50)  # Adjust the transition time as needed
