import socket
import json
import os
from getnanoIDs import get_panel_ids

def start_udp_stream(ip_address, auth_token):
    """
    Start the UDP stream for Nanoleaf control.

    Parameters:
    ip_address (str): IP address of the Nanoleaf device.
    auth_token (str): Authentication token for the device.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # The command to enable extControl UDP streaming
    command = f"{ip_address}/api/v1/{auth_token}/effects"
    message = f"PUT /{command}/extControl"

    # Send the command to the device
    sock.sendto(message.encode(), (ip_address, 60221))

    return "UDP Stream started"

def set_panel_color(ip_address, auth_token, panel_id, r, g, b):
    """
    Set the color of an individual panel.

    Parameters:
    ip_address (str): IP address of the Nanoleaf device.
    auth_token (str): Authentication token for the device.
    panel_id (int): The ID of the panel to be controlled.
    r, g, b (int): Red, Green, and Blue color values (0-255).
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # The command to set the color of an individual panel
    command = f"{ip_address}/api/v1/{auth_token}/panel/{panel_id}"
    message = f"PUT /{command}/rgb/{r},{g},{b}"

    # Send the command to the device
    sock.sendto(message.encode(), (ip_address, 60221))

    return f"Color set for panel {panel_id}"

# Example usage
# start_udp_stream("192.168.1.100", "your_auth_token")
# set_panel_color("192.168.1.100", "your_auth_token", 123, 255, 0, 0) # Set panel 123 to red color

# Note: Replace "192.168.1.100" with the actual IP address of your Nanoleaf device and "your_auth_token" with your actual authentication token. Also, replace 123 with the actual panel ID you want to control.

script_dir = os.path.dirname(os.path.abspath(__file__))
auth_file_path = os.path.join(script_dir, 'auth.json')

def main():
    with open(auth_file_path) as f:
        auth_ip = json.load(f)
    panel_ids = get_panel_ids()
    print(start_udp_stream(auth_ip["ip"], auth_ip["auth"]))

    diff = -1
    r = 0
    g = 0
    b = 0
    while True:
        if r >= 255 or r <= 0:
            diff = -diff
        
        r += diff
        g += diff
        b += diff
        for panel_id in panel_ids:
            print(set_panel_color(auth_ip["ip"], auth_ip["auth"], panel_id, r, g, b))

main()