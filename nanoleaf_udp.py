import struct
import socket
from nanoleafapi import Nanoleaf
import json
import os
import asyncio
import math

script_dir = os.path.dirname(os.path.abspath(__file__))
auth_file_path = os.path.join(script_dir, 'auth.json')

with open(auth_file_path, "r") as f:
    auth_ip = json.load(f)

panel_ids = []

DEVICE_IP = auth_ip["ip"]
AUTH_TOKEN = auth_ip["auth"]

nl = Nanoleaf(DEVICE_IP, auth_token=AUTH_TOKEN)
nl.enable_extcontrol()

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    hlen = len(hex_color)
    return tuple(int(hex_color[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

def create_udp_message(panels_info):
    # Start the message with the number of panels (as a 16-bit integer)
    message = struct.pack('>H', len(panels_info))
    # Append each panel's information
    for panel in panels_info:
        # Pack panel ID in Big Endian format (as a 16-bit integer)
        panel_id = struct.pack('>H', panel['id'])
        # Pack RGB color in Big Endian format (three 8-bit integers)
        color = struct.pack('BBB', *panel['color'])
        # Add a byte for the White channel (not used, so it's zero)
        white_channel = b'\x00'
        # Pack transition time in Big Endian format (as a 16-bit integer)
        transition_time = struct.pack('>H', panel['transition_time'])
        # Append to the message
        message += panel_id + color + white_channel + transition_time
    return message

# Function to send the message via UDP
def send_udp_message(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (ip, port))
    sock.close()

def set_individual_panel_colors(panel_colors, transition_time=3, fade=True):
    transition_time = transition_time if fade else 0
    panels_info = [{'id': panel_id, 'color': hex_to_rgb(panel_color), 'transition_time': transition_time} for panel_id, panel_color in panel_colors.items()]
    udp_message = create_udp_message(panels_info)
    send_udp_message(DEVICE_IP, 60222, udp_message)
