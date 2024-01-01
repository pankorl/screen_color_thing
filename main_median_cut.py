import numpy as np
from PIL import ImageGrab, Image
import tkinter as tk
import sys
import json
from scipy.cluster.vq import kmeans, vq
from nanoleaf import set_individual_panel_colors
from getnanoIDs import get_panel_ids
import io
import random
import cv2

color_history = []  # Global variable to store color history

def color_distance(color1, color2):
    """Calculate the Euclidean distance between two RGB colors."""
    return np.linalg.norm(np.array(color1) - np.array(color2))

def significant_color_change(new_colors, threshold=20):
    """Determine if there's a significant change in colors. Compares new colors to color history."""
    if not color_history:
        return True  # If no history, always update
    
    last_colors = color_history[-1]
    for new_color in new_colors:
        if all(color_distance(new_color, old_color) > threshold for old_color in last_colors):
            return True  # Significant change detected
    return False  # No significant change

def update_color_history(colors):
    """Update the color history with new colors."""
    color_history.append(colors)
    if len(color_history) > 10:  # Keep only recent 10 history states
        color_history.pop(0)

def median_cut_quantize(image, num_colors):
    """Quantize colors using the Median Cut algorithm."""
    pixels = np.array(image).reshape(-1, 3)

    # Filter out 'boring' colors
    exciting_pixels = np.array([pixel for pixel in pixels if not is_boring_color(pixel)])
    
    if exciting_pixels.size == 0:
        return np.array([])  # Return an empty array if no exciting colors found

    centroids, _ = kmeans(exciting_pixels.astype(float), num_colors)
    quantized_colors = centroids.astype(int)
    return quantized_colors



def resize_image(image, resize_factor=0.05):
    """Resize the image by a specified factor."""
    width, height = int(image.width * resize_factor), int(image.height * resize_factor)
    return image.resize((width, height))

def split_image(input_image, partitions):
    """Split the input image into parts as defined by the partitions array."""
    # Load the image
    if isinstance(input_image, str):
        with open(input_image, 'rb') as f:
            image = Image.open(io.BytesIO(f.read()))
    else:
        image = input_image

    # Get the size of the image
    width, height = image.size

    # List to hold the cropped images
    cropped_images = []

    # Process each partition
    for partition in partitions:
        # Calculate pixel coordinates for the partition
        left = partition[0][0] * width
        upper = partition[1][0] * height
        right = partition[0][1] * width
        lower = partition[1][1] * height

        # Crop and append the image
        cropped_images.append(image.crop((left, upper, right, lower)))

    return cropped_images

def on_drag(event):
    """Handle window drag event."""
    x = root.winfo_x() + event.x - click_x
    y = root.winfo_y() + event.y - click_y
    root.geometry(f"+{x}+{y}")

def on_click(event):
    """Handle window click event."""
    global click_x, click_y
    click_x = event.x
    click_y = event.y

def calculate_luminosity(color):
    """Calculate the luminosity of a given RGB color."""
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

def sort_colors_by_luminosity(colors):
    """Sort a list of RGB colors by luminosity."""
    return sorted(colors, key=calculate_luminosity, reverse=True)

def rgb_to_hsv(color):
    """Convert an RGB color to HSV."""
    color = np.uint8([[color]])
    hsv_color = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
    return hsv_color[0][0]

def is_boring_color(color, saturation_threshold=25, value_thresholds=(50, 205)):
    """
    Check if a color is considered 'boring', which means it's either too greyish, too dark, or too bright.
    Saturation below a certain threshold indicates greyness.
    Value (brightness) too high or too low indicates white or black.
    """
    hsv_color = rgb_to_hsv(color)
    hue, saturation, value = hsv_color
    return saturation < saturation_threshold or value < value_thresholds[0] or value > value_thresholds[1]

def main():
    num_clusters = 3
    partitions = [[[0, 1], [0, 1]]]
    sim_color_thres = 10

    global root
    if config["show_visual"]:
        root = tk.Tk()
        root.overrideredirect(True)
        root.configure(bg='black')
        root.title("Cluster Colors")
        window_height = 120
        window_width = 20
        root.geometry(f"{window_width}x{window_height}")
        root.bind('<Button-1>', on_click)
        root.bind('<B1-Motion>', on_drag)
        root.attributes('-topmost', True)
        canvas = tk.Canvas(root, width=window_width, height=window_height)
        canvas.pack()

    if config["use_nanoleaf"]:
        panel_ids = get_panel_ids()
        random.shuffle(panel_ids)
        num_clusters = len(panel_ids)

    print("Running...")
    while True:
        screen = ImageGrab.grab(all_screens=True)
        screen_partitions = split_image(screen, partitions)

        # if config["show_visual"]:
        #     canvas.delete("all")

        hex_colors = []
        for partition, screen_partition in zip(partitions, screen_partitions):
            screen_partition = resize_image(screen_partition)
            dom_colors = median_cut_quantize(screen_partition, num_clusters)
            dom_colors = sort_colors_by_luminosity(dom_colors)

            if significant_color_change(dom_colors, sim_color_thres*num_clusters):
                
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

        if significant_color_change(dom_colors, sim_color_thres*num_clusters):
            update_color_history(dom_colors)
            if config["use_nanoleaf"]:
                panel_colors = {}
                for panel_id_, color_hex in zip(panel_ids, hex_colors):
                    panel_colors[panel_id_] = color_hex
                set_individual_panel_colors(panel_colors)

        if config["show_visual"]:
            root.update_idletasks()
            root.update()

if __name__ == "__main__":
    print("Starting...")
    if len(sys.argv) == 1:
        print("Using config.json")
        with open("config.json", "r") as f:
            config = json.load(f)
    else:
        config = {}
        config["use_nanoleaf"] = True if sys.argv.count("nl") > 0 else False
        config["show_visual"] = True if sys.argv.count("gui") > 0 else False
        print(f"Config: {config}")
    main()
