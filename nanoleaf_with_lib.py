from nanoleafapi import Nanoleaf
import json
import os
import asyncio
import math


script_dir = os.path.dirname(os.path.abspath(__file__))
auth_file_path = os.path.join(script_dir, 'auth.json')

with open(auth_file_path, "r") as f:
    auth_ip = json.load(f)

DEVICE_IP = auth_ip["ip"]
AUTH_TOKEN = auth_ip["auth"]


nl = Nanoleaf(DEVICE_IP, auth_token=AUTH_TOKEN)
nl.enable_extcontrol()


# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    hlen = len(hex_color)
    return tuple(int(hex_color[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

# Function to create effect data for a single panel with transition time
def create_single_panel_effect_data(panel_id, rgb_color, transition_time=50, fade=True):
    # Panel data string for one panel with transition time for fade effect
    if not fade:
        transition_time = 0
    panel_data = f"1 {panel_id} 1 {rgb_color[0]} {rgb_color[1]} {rgb_color[2]} 0 {transition_time}"
    return panel_data

def create_multiple_panel_effect_data(panel_colors, transition_time=50, fade=True):
    # Set transition time to 0 if fade is False
    if not fade:
        transition_time = 0

    effect_data = f"{len(panel_colors)} "
    for panel_id, hex_color in panel_colors.items():
        rgb_color = hex_to_rgb(hex_color) if isinstance(hex_color, str) else hex_color
        effect_data += f"{panel_id} 1 {rgb_color[0]} {rgb_color[1]} {rgb_color[2]} 0 {transition_time} "
    return effect_data.strip()

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


# Function to set individual panel colors with a delay between each to prevent blocking
async def set_individual_panel_colors_(panel_colors, transition_time=3, fade=True):
    transition_time = 3 if fade else 0
    effect_data = create_multiple_panel_effect_data(panel_colors, transition_time=transition_time, fade=fade)
    await send_effect_data(effect_data)

async def set_individual_panel_colors_nofade(data):
    set_individual_panel_colors_(data, fade=False)


async def set_individual_panel_colors(data, fade=True):
    await set_individual_panel_colors_(data, fade=fade)