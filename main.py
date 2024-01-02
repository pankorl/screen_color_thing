from logging import root
import numpy as np
import tkinter as tk
import time
# from nanoleaf_with_lib import set_individual_panel_colors, nl
from nanoleaf_udp import set_individual_panel_colors, nl
from getnanoIDs import get_panel_ids
import json
import sys
import os
import asyncio
from screencap import capture_screen
from color_picker import get_colors_from_image, get_colors_from_screen, significant_color_change
from screen_partitioning import split_image


script_dir = os.path.dirname(os.path.abspath(__file__))
color_history = []  # Global variable to store color history

def update_color_history(colors):
    """
    Update the color history with new colors.
    """
    color_history.append(colors)
    if len(color_history) > 10:  # Keep only recent 10 history states
        color_history.pop(0)

def on_drag(event):
    x = root.winfo_x() + event.x - click_x
    y = root.winfo_y() + event.y - click_y
    root.geometry(f"+{x}+{y}")

def on_click(event):
    global click_x, click_y
    click_x = event.x
    click_y = event.y


async def main():
    # init()
    num_clusters = 3
    color_similarity_thresh = 100
    bin_size = 30
    partitions = config['screen_partitions']
    if len(partitions) == 0:
        # partitions = [[[0,1],[0,1]]]
        partitions = [None]

    global root
    if config["show_visual"]:
        root = tk.Tk()  
        root.overrideredirect(True)
        root.configure(bg='black')
        root.title("Cluster Colors")
        window_height = 120
        window_width = 20
        root.geometry(f"{window_width}x{window_height}")  # Set the window size to be big enough to hold all partitions
        # Bind the click and drag events
        root.bind('<Button-1>', on_click)
        root.bind('<B1-Motion>', on_drag)
        root.attributes('-topmost', True)
        canvas = tk.Canvas(root, width=window_width, height=window_height)
        canvas.pack()

    if config["use_nanoleaf"]:
        panel_ids = get_panel_ids()
        num_clusters = len(panel_ids)
        if nl.enable_extcontrol():
            print("extcontrol enabled")
        else:
            print("extcontrol failed")

    window_name = None  # Replace with the actual window name
    screen_width = 1920  # Replace with your screen width
    screen_height = 1080  # Replace with your screen height

    print("Running...")
    while True:
        time.sleep(0.1)
        # screen = ImageGrab.grab(all_screens=True)
        # screen.save("screencap.png")

        if partitions[0] == None:
            screen_partitions = [None]
        else:
            screen = capture_screen(window_name, screen_width, screen_height)
            screen_partitions = split_image(screen, partitions)

        if config["show_visual"]:
            canvas.delete("all")

        hex_colors = []
        for partition, screen_partition in zip(partitions, screen_partitions):

            if partition == None:
                dom_colors = get_colors_from_screen(bin_size, num_clusters, similarity_threshold=color_similarity_thresh, min_color_amnt=config['min_color_amnt'])
            else:
                dom_colors = get_colors_from_image(screen_partition, bin_size, num_clusters, similarity_threshold=color_similarity_thresh, min_color_amnt=config['min_color_amnt'])

            if config["show_visual"]:
                # Calculate the position of the partition on the canvas
                left = partition[0][0] * window_width
                top = partition[1][0] * window_height
                right = partition[0][1] * window_width
                bottom = partition[1][1] * window_height
                partition_height = bottom - top

            # Draw the dominant colors for this partition
            for i, color in enumerate(dom_colors):
                color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
                hex_colors.append(color_hex)
                if config["show_visual"]:
                    color_height = partition_height / len(dom_colors)
                    color_top = top + (i * color_height)
                    color_bottom = top + ((i + 1) * color_height)
                    canvas.create_rectangle(left, color_top, right, color_bottom, fill=color_hex, outline=color_hex)

        if config["use_nanoleaf"]:
            panel_colors = {}   
            for panel_id_, i in zip(panel_ids,range(len(panel_ids))):
                panel_colors[panel_id_] = hex_colors[i]

            # Check for significant color change
            if  not config["less_sensitive"] and significant_color_change(hex_colors, color_history, threshold=80):
                # If significant color change detected, update colors without fading
                await set_individual_panel_colors(panel_colors, fade=False)
            else:
                # No significant change or less sensitive, update colors with fading
                await set_individual_panel_colors(panel_colors, fade=True) 
            update_color_history(hex_colors)
            # await set_individual_panel_colors(panel_colors)
            # asyncio.run(start_fade(panel_colors, 3))

        if config["show_visual"]:
            root.update_idletasks()
            root.update()

if __name__ == "__main__":
    config_file_path = os.path.join(script_dir, 'config.json')
    print("Starting...")
    with open(config_file_path, "r") as f:
        config = json.load(f)
    if len(sys.argv) == 1:
        print("Using config.json")
    else:
        config["use_nanoleaf"] = True if sys.argv.count("nl") > 0 else False
        config["show_visual"] = True if sys.argv.count("gui") > 0 else False
        print(f"Config: {config}")
    asyncio.run(main())
