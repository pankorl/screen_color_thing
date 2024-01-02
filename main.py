from logging import root
import cv2
import numpy as np
from PIL import ImageGrab, Image
import tkinter as tk
import time
import io
from kmodes.kmodes import KModes
from nanoleaf_with_lib import set_individual_panel_colors, nl
# from nanoleaf_udp import set_individual_panel_colors, nl
from getnanoIDs import get_panel_ids
import numpy as np
from PIL import Image
import json
import sys
import os
import asyncio
from screencap import capture_screen

script_dir = os.path.dirname(os.path.abspath(__file__))

color_history = []  # Global variable to store color history

def hex_to_rgb(hex_color):
    """Convert a hexadecimal color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(color1, color2):
    """Calculate the Euclidean distance between two RGB colors."""
    if isinstance(color1, str):
        color1 = hex_to_rgb(color1)
    if isinstance(color2, str):
        color2 = hex_to_rgb(color2)
    return np.linalg.norm(np.array(color1) - np.array(color2))


def significant_color_change(new_colors, threshold=10):
    """
    Determine if there's a significant change in colors.
    Compares new colors to color history.
    """
    if not color_history:
        return True  # If no history, always update
    
    last_colors = color_history[-1]
    for new_color in new_colors:
        if all(color_distance(new_color, old_color) > threshold for old_color in last_colors):
            return True  # Significant change detected
    return False  # No significant change

def update_color_history(colors):
    """
    Update the color history with new colors.
    """
    color_history.append(colors)
    if len(color_history) > 10:  # Keep only recent 10 history states
        color_history.pop(0)

def is_color_greyish(color, grey_tolerance=20):
    """
    Check if a color is close to grey.
    A color is considered 'greyish' if the R, G, and B values are within a certain range of each other.
    """
    r, g, b = color
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    return (max_val - min_val) <= grey_tolerance

def quantize_color_and_sort_by_brightness(image, bin_size, num_colors=5, similarity_threshold=30, min_color_amnt=16):
    """
    outputs the most interesting colors.
    """
    # Convert the image to numpy array
    data = np.array(image)
    
    # binning
    quantized = data // bin_size * bin_size
    
    # get bins with counts
    colors, counts = np.unique(quantized.reshape(-1, 3), axis=0, return_counts=True)
    
    colors = np.array([color for color, count in zip(colors, counts) if count > min_color_amnt])
    counts = np.array([count for count in counts if count > min_color_amnt])

    # sort bins by count
    sorted_indices = np.argsort(counts)[::-1]
    most_frequent_colors = colors[sorted_indices]

    # filter by luminoscity
    # brighter_colors = [color for color in most_frequent_colors if 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2] > brightness_threshold]

    # Remove greyish colors
    no_gray_colors = [color for color in most_frequent_colors if not is_color_greyish(color)]
    unique_colors = []

    # Remove colors that are too similar
    for color in no_gray_colors:
        if not any(color_distance(color, unique_color) < similarity_threshold for unique_color in unique_colors):
            unique_colors.append(color)
    
    i = 0
    while len(unique_colors) < num_colors:
        try:
            unique_colors.append(most_frequent_colors[i])
        except:
            unique_colors.append([10*i, 10*i, 10*i])
        i+=1
    
    # If there's a significant color change, update the color history
    if not config["less_sensitive"] or significant_color_change(unique_colors):
        if config["less_sensitive"]:
            update_color_history(unique_colors)
        return unique_colors[:num_colors]
    else:
        # Return the last known good color set if no significant change
        return color_history[-1][:num_colors] if color_history else unique_colors[:num_colors]

def resize_image(image, resize_factor=0.1):
    """
    Resizes input image to 10% the size (1% of the total pixel count)

    :param image: input image.
    :param resize_factor: default to 0.1 (10%)
    """
    width, height = int(image.width * resize_factor), int(image.height * resize_factor)
    return image.resize((width, height))

def split_image(input_image, partitions):
    """
    Splits the input image into parts as defined by the partitions array.

    :param input_image: An image file or PIL image object.
    :param partitions: An array of partitions, each defined by fractional start and end points.
    :return: A list of cropped image parts.
    """
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
    x = root.winfo_x() + event.x - click_x
    y = root.winfo_y() + event.y - click_y
    root.geometry(f"+{x}+{y}")

def on_click(event):
    global click_x, click_y
    click_x = event.x
    click_y = event.y

def calculate_color_contrast_level(image):
    """
    Calculate the contrast level of an image based on the variance of color distances.
    """
    data = np.array(image)
    n_pixels = data.shape[0] * data.shape[1]

    # Compute mean color of the image
    mean_color = np.mean(data.reshape(n_pixels, 3), axis=0)

    # Calculate the Euclidean distance of each pixel's color from the mean color
    color_distances = np.linalg.norm(data.reshape(n_pixels, 3) - mean_color, axis=1)

    # Calculate the variance of these distances
    variance = np.var(color_distances)
    return variance


def calculate_luminosity(color):
    """Calculate the luminosity of a given RGB color."""
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

def sort_colors_by_luminosity(colors):
    """Sort a list of RGB colors by luminosity."""
    return sorted(colors, key=calculate_luminosity, reverse=True)


async def main():
    # init()
    num_clusters = 3
    color_similarity_thresh = 100
    bin_size = 30
    partitions = [[[0,1],[0,1]]]

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
        screen = capture_screen(window_name, screen_width, screen_height)
        # screen.save("screencap.png")

        screen_partitions = split_image(screen, partitions)
        contrast_levels = [calculate_color_contrast_level(partition) for partition in screen_partitions]

        if config["show_visual"]:
            canvas.delete("all")

        hex_colors = []
        for partition, screen_partition, contrast in zip(partitions, screen_partitions, contrast_levels):
            # screen_partition = resize_image(screen_partition)

            adjusted_similarity_thresh = color_similarity_thresh + (contrast / 1000)
            dom_colors = quantize_color_and_sort_by_brightness(screen_partition, bin_size, num_clusters, similarity_threshold=adjusted_similarity_thresh, min_color_amnt=config['min_color_amnt'])

            dom_colors = sort_colors_by_luminosity(dom_colors)

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
            if  not config["less_sensitive"] and significant_color_change(hex_colors, threshold=80):
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
