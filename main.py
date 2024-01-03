import time
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
from PyQt5.QtCore import pyqtSignal, QThread
from colorset_events import color_set_event_handler, init_event_handler, get_ids


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

    global overlay
    overlay = None


    def pause_from_menu():
        worker.pause()
        pauseAction.setVisible(False)
        unpauseAction.setVisible(True)

    def unpause_from_menu():
        worker.unpause()
        unpauseAction.setVisible(False)
        pauseAction.setVisible(True)

    # def toggle_overlay():
    #     global overlay
    #     toggleOverlayAction.setChecked(not toggleOverlayAction.isChecked())
    #     config['show_visual'] = not config['show_visual']
    #     if overlay is None:
    #         overlay = init_overlay()
    #     if not config['show_visual']:
    #         overlay.destroy()

    
    pauseAction = menu.addAction("Pause")
    pauseAction.triggered.connect(pause_from_menu)
    unpauseAction = menu.addAction("Start")
    unpauseAction.triggered.connect(unpause_from_menu)

    # toggleOverlayAction = menu.addAction("Toggle overlay")
    # toggleOverlayAction.setCheckable(True)
    # toggleOverlayAction.triggered.connect(toggle_overlay)
    # toggleOverlayAction.setChecked(config['show_visual'])

    unpauseAction.setVisible(False)

    trayIcon.setContextMenu(menu)
    trayIcon.show()

    # if config['show_visual'] and not overlay:
    #     overlay = init_overlay()

    
    worker = Worker()
    # worker.update_signal.connect(handle_update)
    worker.start()

    app.exec_()

# def init_overlay():
#     gui_wh = config["gui_w_h"]
#     return Overlay(gui_wh[0], gui_wh[1])

# def handle_update(partitions, all_dom_colors):
#     global overlay
#     # This function will be executed in the main thread
#     # Call your draw_partitions method here
#     overlay.draw_partitions(partitions, all_dom_colors)

class Worker(QThread):
    update_signal = pyqtSignal(object, object)
    def run(self):
        self.paused = False
        num_clusters = config["default_num_colors"]
        color_similarity_thresh = 100
        bin_size = 30
        partitions = config['screen_partitions']

        if len(partitions) == 0:
            # partitions = [[[0,1],[0,1]]]
            partitions = [None]

        if config["show_visual"]:
            self.gui_wh = config["gui_w_h"]
            self.overlay = Overlay(self.gui_wh[0], self.gui_wh[1])

        if config["use_lights"]:
            panel_ids = get_ids(config['lights_type'])
            num_clusters = len(panel_ids)
            init_event_handler(config['lights_type'])

        screen_width = 1920
        screen_height = 1080

        print("Running...")

        while True:
            if self.paused:
                time.sleep(0.5)
                continue
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
                # self.update_signal.emit(partitions, all_dom_colors)
                self.overlay.draw_partitions(partitions, all_dom_colors)

            if config["use_lights"]:
                panel_colors = {}   
                for panel_id_, i in zip(panel_ids,range(len(panel_ids))):
                    panel_colors[panel_id_] = hex_colors[i]

                # Check for significant color change
                if  not config["less_sensitive"] and significant_color_change(hex_colors, color_history, threshold=config["quick_change_thresh"]):
                    # If significant color change detected, update colors without fading
                    color_set_event_handler(config['lights_type'], panel_colors, 0)
                else:
                    # No significant change or less sensitive, update colors with fading
                    color_set_event_handler(config['lights_type'], panel_colors, config['transition_time']) 
                update_color_history(hex_colors)

    def pause(self):
        self.paused = True
  
    def unpause(self):
        """
        unpause
        """
        self.paused = False


if __name__ == "__main__":
    config_file_path = os.path.join(script_dir, 'config.json')
    print("Starting...")
    with open(config_file_path, "r") as f:
        config = json.load(f)
    if len(sys.argv) == 1:
        print("Using config.json")
    else:
        config["use_lights"] = True if sys.argv.count("nl") > 0 else False
        config["show_visual"] = True if sys.argv.count("gui") > 0 else False
        config["less_sensitive"] = True if sys.argv.count("ls") > 0 else False
        print(f"Config: {config}")
    asyncio.run(main())
