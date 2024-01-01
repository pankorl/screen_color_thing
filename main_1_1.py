from logging import root
import cv2
import numpy as np
from PIL import ImageGrab, Image
import tkinter as tk
import time
import io
from kmodes.kmodes import KModes
from nanoleaf import set_individual_panel_colors
from getnanoIDs import get_panel_ids
import numpy as np
from PIL import Image
import json
import sys


def get_dominant_color(image, k=5, resize_factor=0.01):
    # Resize the image
    width, height = int(image.width * resize_factor), int(image.height * resize_factor)
    image = image.resize((width, height))

    # Convert image to OpenCV format and then to a list of pixels
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    pixels = image.reshape(-1, 3)

    # Convert to floating point for OpenCV k-means function
    pixels = np.float32(pixels)

    # Define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Count labels to find the most common cluster
    _, counts = np.unique(labels, return_counts=True)

    # Combine centers with their counts
    combined = list(zip(centers, counts))
    
    # Sort based on counts
    combined.sort(key=lambda x: x[1], reverse=True)
    
    # Extract sorted centers
    sorted_centers = [x[0] for x in combined]
    
    # Convert color to RGB format
    sorted_centers = [color[::-1] for color in sorted_centers]
    return sorted_centers

    # Convert color to RGB format
    dominant_color = dominant_color[::-1]
    return dominant_color

def get_dominant_color_sorted_by_brightness(image, k=5, resize_factor=0.01):
    # Resize the image
    width, height = int(image.width * resize_factor), int(image.height * resize_factor)
    image = image.resize((width, height))

    # Convert image to OpenCV format and then to a list of pixels
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    pixels = image.reshape(-1, 3)

    # Convert to floating point for OpenCV k-means function
    pixels = np.float32(pixels)

    # Define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert centers to RGB format and calculate brightness
    centers = [center[::-1] for center in centers]  # BGR to RGB
    brightness = [0.299*color[0] + 0.587*color[1] + 0.114*color[2] for color in centers]  # Calculate brightness

    # Combine centers with their brightness
    combined = list(zip(centers, brightness))
    
    # Sort based on brightness
    combined.sort(key=lambda x: x[1], reverse=True)
    
    # Extract sorted centers
    sorted_centers = [x[0] for x in combined]
    
    return sorted_centers

def update_color_display(window, color):
    color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
    window.config(bg=color_hex)

def get_dominant_color_sorted_by_saturation(image, k=5, resize_factor=0.01):
    # Resize the image
    width, height = int(image.width * resize_factor), int(image.height * resize_factor)
    image = image.resize((width, height))

    # Convert image to OpenCV format and then to a list of pixels
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    pixels = image.reshape(-1, 3)

    # Convert to floating point for OpenCV k-means function
    pixels = np.float32(pixels)

    # Define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert centers to HSV format and calculate saturation
    centers = [cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0] for color in centers]

    # Sort by the saturation value (the 'S' in HSV)
    centers.sort(key=lambda x: x[1], reverse=True)
    
    # Convert sorted centers back to RGB format
    sorted_centers = [cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_HSV2RGB)[0][0] for color in centers]
    
    return sorted_centers

def get_dominant_color_mode(image, k=5, resize_factor=0.01):
    # Resize the image
    width, height = int(image.width * resize_factor), int(image.height * resize_factor)
    image = image.resize((width, height))

    # Convert image to OpenCV format and then to a list of pixels
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    pixels = image.reshape(-1, 3)

    # Initialize the k-modes
    km = KModes(n_clusters=k, init='Huang', n_init=k, verbose=1)
    clusters = km.fit_predict(pixels)

    # Find the modes
    modes = km.cluster_centroids_
    modes = modes.astype(int)

    # Convert modes to RGB format
    modes = [color[::-1] for color in modes]  # BGR to RGB
    return modes

def resize_image(image, resize_factor=0.1):
    width, height = int(image.width * resize_factor), int(image.height * resize_factor)
    return image.resize((width, height))

def quantize_color(image, bin_size):
    """Quantize the colors by binning them"""
    # Convert the image to numpy array
    data = np.array(image)
    
    # Floor the color values to the nearest bin
    quantized = data // bin_size * bin_size
    
    # Get the unique colors and counts
    colors, counts = np.unique(quantized.reshape(-1, 3), axis=0, return_counts=True)
    
    # Sort colors by counts
    sorted_indices = np.argsort(counts)[::-1]
    sorted_colors = colors[sorted_indices]
    
    # Return the most frequent colors
    return sorted_colors[:5]

import numpy as np

def color_distance(color1, color2):
    """Calculate the Euclidean distance between two RGB colors."""
    return np.linalg.norm(np.array(color1) - np.array(color2))

def remove_similar_colors(colors, threshold=30, min_colors = 2):
    """Remove colors that are too similar to each other from the list."""
    unique_colors = []
    while True:
        for color in colors:
            if not unique_colors:  # If unique_colors is empty, add the first color
                unique_colors.append(color)
                continue
            # If color is different enough from all unique colors, add it to the list
            if all(color_distance(color, unique_color) > threshold for unique_color in unique_colors):
                unique_colors.append(color)
        if len(unique_colors) < min_colors:
            threshold -= 10
        else:
            break
        if threshold < 10:
            return colors
    return unique_colors

def rgb_to_hsv(rgb_colors):
    """Convert an array of RGB colors to HSV."""
    hsv_colors = cv2.cvtColor(np.uint8([rgb_colors]), cv2.COLOR_RGB2HSV)
    return hsv_colors[0]  # cv2 adds an extra dimension

def quantize_color_and_sort_by_brightness(image, bin_size, num_colors=5, brightness_threshold=60, similarity_threshold=30):
    """Quantize the colors by binning them, sort the top colors by brightness, and remove similar colors."""
    # Convert the image to numpy array
    data = np.array(image)
    
    # Floor the color values to the nearest bin
    quantized = data // bin_size * bin_size
    
    # Get the unique colors and counts
    colors, counts = np.unique(quantized.reshape(-1, 3), axis=0, return_counts=True)
    
    # Sort colors by counts
    sorted_indices = np.argsort(counts)[::-1]
    most_frequent_colors = colors[sorted_indices]
    # Filter out dark colors by brightness threshold
    # brighter_colors = most_frequent_colors[brightness > brightness_threshold]
    # brighter_colors = most_frequent_colors

    # # If there aren't enough bright colors, reduce the threshold until there are
    # while len(brighter_colors) < num_colors and brightness_threshold > 0:
    #     brightness_threshold -= 5
    #     brighter_colors = most_frequent_colors[brightness > brightness_threshold]

    # Remove similar colors
    # print(len(brighter_colors))

    

    filtered_colors = remove_similar_colors(most_frequent_colors, threshold=similarity_threshold, min_colors=num_colors)
    print(len(filtered_colors))
    filtered_colors = np.array(filtered_colors)

    if config["sort_by_luminoscity"]:
        # Calculate brightness of each color
        brightness = 0.299 * filtered_colors[:, 0] + 0.587 * filtered_colors[:, 1] + 0.114 * filtered_colors[:, 2]
        
        # Sort the remaining colors by brightness
        brightness_sorted_indices = np.argsort(brightness)[::-1]
        brightest_colors = filtered_colors[brightness_sorted_indices]
        return brightest_colors[:num_colors]
    elif config["sort_by_saturation"]:
        # Convert filtered RGB colors to HSV
        hsv_colors = rgb_to_hsv(filtered_colors)

        # Extract the Saturation component (S in HSV)
        saturation = hsv_colors[:, 1]

        # Sort the remaining colors by saturation (from highest to lowest)
        saturation_sorted_indices = np.argsort(saturation)[::-1]
        most_saturated_colors = filtered_colors[saturation_sorted_indices]

        # If there are still too many colors, truncate the list
        most_saturated_colors = most_saturated_colors[:num_colors]  # Ensuring only the top 'num_colors' are returned

        return most_saturated_colors
    
    else:
        return filtered_colors[:num_colors]
    

    # If there are still too many colors, truncate the list
    print(len(brightest_colors))
    return filtered_colors[:num_colors]


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

def main():
    num_clusters = 3

    color_similarity_thresh = 200
    bin_size = 30

    # partitions = [[[0,0.5],[0,0.5]],[[0.5,1],[0,0.5]],[[0,0.5],[0.5,1]],[[0.5,1],[0.5,1]]]
    # partitions = [[[0,1],[0,0.5]],[[0,1],[0.5,1]]]
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

    print("Running...")
    while True:
        screen = ImageGrab.grab(all_screens=True)
        screen_partitions = split_image(screen, partitions)
        if config["show_visual"]:
            canvas.delete("all")  # Clear the canvas before redrawing
        hex_colors = []

        for partition, screen_partition in zip(partitions, screen_partitions):
            screen_partition = resize_image(screen_partition)
            dom_colors = quantize_color_and_sort_by_brightness(screen_partition, bin_size, num_clusters, similarity_threshold=color_similarity_thresh)
            # dom_colors = get_dominant_color_mode(screen_partition, k=num_clusters, resize_factor=0.1)

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
            set_individual_panel_colors(panel_colors)

        if config["show_visual"]:
            root.update_idletasks()
            root.update()
        # time.sleep(0.2)


if __name__ == "__main__":
    print("Starting...")
    if len(sys.argv) == 1:
        print("Using config.json")
        with open("config.json", "r") as f:
            config = json.load(f)
        main()
    else:
        config = {}
        config["use_nanoleaf"] = True if sys.argv.count("nl") > 0 else False
        config["show_visual"] = True if sys.argv.count("gui") > 0 else False
        print(f"Config: {config}")
        main()