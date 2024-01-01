from nanoleafapi import Nanoleaf
import json
import os
import asyncio
import math

prev_color = (0,0,0)

# def init():
# global nl
# global prev_color
script_dir = os.path.dirname(os.path.abspath(__file__))
auth_file_path = os.path.join(script_dir, 'auth.json')

with open(auth_file_path, "r") as f:
    auth_ip = json.load(f)

DEVICE_IP = auth_ip["ip"]
AUTH_TOKEN = auth_ip["auth"]

prev_color = (0,0,0)

fade_counter = 0
prev_colors = []


nl = Nanoleaf(DEVICE_IP, auth_token=AUTH_TOKEN)

nl.enable_extcontrol()

async def set_individual_panel_colors_flow(panel_colors: dict, transition_time=0.1):
    global nl
    global prev_color
    rgb = tuple(int(panel_colors[57011][1:][i:i+2], 16) for i in (0, 2, 4))
    # nl.set_color((255, 0, 0))
    # nl.flow([prev_color, rgb], transition_time)
    prev_color = rgb
    nl.set_color(rgb)
    # nl.write_e
    return True

# def create_effect_data_flow():
#     effect_json = {
#         "command": "displayTemp",
#         "animType": "solid",
#         "palette": [
#             {
#             "hue": 0,
#             "saturation": < user >,
#             "brightness": < user >
#             }
#         ],
#         "colorType": "HSB"
#         }

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    hlen = len(hex_color)
    return tuple(int(hex_color[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

# Function to create effect data for a single panel with transition time
def create_single_panel_effect_data(panel_id, rgb_color, transition_time=50):
    # Panel data string for one panel with transition time for fade effect
    panel_data = f"1 {panel_id} 1 {rgb_color[0]} {rgb_color[1]} {rgb_color[2]} 0 {transition_time}"
    return panel_data

def create_multiple_panel_effect_data(panel_ids, rgb_colors, transition_frames=10):
    panel_data = f"{len(panel_ids)} "
    for panel_id, rgb_color in zip(panel_ids, rgb_colors):
        panel_data += f"{transition_frames} {rgb_color[0]} {rgb_color[1]} {rgb_color[2]} 0 0 "

# Function to send effect data for a single panel
async def send_effect_data(effect_data):
    effect_json = {
        "command": "display",
        "version": "2.0",
        "animType": "static",
        "animData": effect_data,
        "loop": False,
        "palette": []
    }
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, nl.write_effect, effect_json)
    # nl.write_effect(effect_json)


    # url = f"http://{DEVICE_IP}:16021/api/v1/{AUTH_TOKEN}/effects"
    # headers = {'Content-Type': 'application/json'}

    # response = requests.put(url, data=json.dumps({"write": effect_json}), headers=headers)
    # if response.status_code not in [200, 204]:
        # print(f"HTTP Error: Status code {response.status_code}")
        # print(f"Response: {response.text}")

# Function to set individual panel colors with fade
async def set_individual_panel_colors_old(panel_colors, transition_time=100):
    for panel_id, hex_color in panel_colors.items():
        if len(hex_color) != 3:
            rgb_color = hex_to_rgb(hex_color)
        else:
            rgb_color = hex_color
        effect_data = create_single_panel_effect_data(panel_id, rgb_color, transition_time)
        await send_effect_data(effect_data)

# Function to set individual panel colors with a delay between each to prevent blocking
async def set_individual_panel_colors_(panel_colors, transition_time=3, delay=0.005):
    for panel_id, hex_color in panel_colors.items():
        if len(hex_color) != 3:
            rgb_color = hex_to_rgb(hex_color)
        else:
            rgb_color = hex_color
        effect_data = create_single_panel_effect_data(panel_id, rgb_color, transition_time)
        await send_effect_data(effect_data)
        await asyncio.sleep(delay)  # Wait for a short period before sending the next request



async def start_fade(new_panel_colors: dict, fade_time=3):
    global prev_colors
    fade_counter = 0
    new_colors = [hex_to_rgb(panel_color) for _, panel_color in new_panel_colors.items()]
    if len(prev_colors) != len(new_colors):
        prev_colors = [(0,0,0) for _ in new_colors]
    panel_ids = [panel_id for panel_id, _ in new_panel_colors.items()]
    delta_colors = [[new_value-old_value for new_value, old_value in zip(new_color, old_color)] for new_color, old_color in zip(new_colors, prev_colors)]
    inc_colors = [[math.floor(delta_value/fade_time) for delta_value in delta_color] for delta_color in delta_colors]
    while fade_counter < fade_time:
        fade_counter += 1

        prev_colors = [(prev_color_[0]+inc_color[0],prev_color_[1]+inc_color[1],prev_color_[2]+inc_color[2]) for prev_color_, inc_color in zip(prev_colors, inc_colors)]
        send_data = {panel_id: panel_color for panel_id, panel_color in zip(panel_ids, prev_colors)}
        await set_individual_panel_colors(send_data)
        if fade_counter == 0:
            break


async def set_individual_panel_colors(data, fade=True):
    if fade:
        await set_individual_panel_colors_(data)
    # else:
        # await set_individual_panel_colors_nofade(data)