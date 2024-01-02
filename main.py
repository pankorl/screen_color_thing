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
from screencap import capture_screen_scaled
from color_picker import get_colors_from_image, get_colors_from_screen, significant_color_change
from screen_partitioning import split_image
from overlay import Overlay
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread


script_dir = os.path.dirname(os.path.abspath(__file__))
color_history = []  # Global variable to store color history

def update_color_history(colors):
    """
    Update the color history with new colors.
    """
    color_history.append(colors)
    if len(color_history) > 10:  # Keep only recent 10 history states
        color_history.pop(0)

async def main():
    app = QApplication(sys.argv)
    icon_file_path = os.path.join(script_dir, 'nlmirror.ico')
    trayIcon = QSystemTrayIcon(QIcon(icon_file_path), app)
    menu = QMenu()

    exitAction = menu.addAction("Exit")
    exitAction.triggered.connect(app.quit)
    
    trayIcon.setContextMenu(menu)
    trayIcon.show()
    
    worker = Worker()
    worker.start()

    app.exec_()


class Worker(QThread):
    def run(self):
        num_clusters = config["default_num_colors"]
        color_similarity_thresh = 100
        bin_size = 30
        partitions = config['screen_partitions']

        if len(partitions) == 0:
            # partitions = [[[0,1],[0,1]]]
            partitions = [None]

        if config["show_visual"]:
            overlay = Overlay(20, 120)

        if config["use_nanoleaf"]:
            panel_ids = get_panel_ids()
            num_clusters = len(panel_ids)
            if nl.enable_extcontrol():
                print("extcontrol enabled")
            else:
                print("extcontrol failed")

        screen_width = 1920
        screen_height = 1080

        print("Running...")

        while True:
            time.sleep(0.1)

            all_dom_colors = []
            hex_colors = []

            if partitions[0] == None:
                screen_partitions = [None]
            else:
                screen = capture_screen_scaled(screen_width, screen_height)
                screen_partitions = split_image(screen, partitions)

            for partition, screen_partition in zip(partitions, screen_partitions):
                if partition == None:
                    dom_colors = get_colors_from_screen(bin_size, num_clusters, similarity_threshold=color_similarity_thresh, min_color_amnt=config['min_color_amnt'])
                else:
                    dom_colors = get_colors_from_image(screen_partition, bin_size, num_clusters, similarity_threshold=color_similarity_thresh, min_color_amnt=config['min_color_amnt'])

                all_dom_colors.append(dom_colors)

                # Get hex colors
                for i, color in enumerate(dom_colors):
                    color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
                    hex_colors.append(color_hex)

            if config["show_visual"]:
                overlay.draw_partitions(partitions, all_dom_colors)

            if config["use_nanoleaf"]:
                panel_colors = {}   
                for panel_id_, i in zip(panel_ids,range(len(panel_ids))):
                    panel_colors[panel_id_] = hex_colors[i]

                # Check for significant color change
                if  not config["less_sensitive"] and significant_color_change(hex_colors, color_history, threshold=config["quick_change_thresh"]):
                    # If significant color change detected, update colors without fading
                    set_individual_panel_colors(panel_colors, config['transition_time'], fade=False)
                else:
                    # No significant change or less sensitive, update colors with fading
                    set_individual_panel_colors(panel_colors, config['transition_time'], fade=True) 
                update_color_history(hex_colors)
  

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
        config["less_sensitive"] = True if sys.argv.count("ls") > 0 else False
        print(f"Config: {config}")
    asyncio.run(main())


