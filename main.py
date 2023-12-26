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

def quantize_color_and_sort_by_brightness(image, bin_size, num_colors=5):
    """Quantize the colors by binning them and then sort the top colors by brightness"""
    # Convert the image to numpy array
    data = np.array(image)
    
    # Floor the color values to the nearest bin
    quantized = data // bin_size * bin_size
    
    # Get the unique colors and counts
    colors, counts = np.unique(quantized.reshape(-1, 3), axis=0, return_counts=True)
    
    # Sort colors by counts
    sorted_indices = np.argsort(counts)[::-1]
    most_frequent_colors = colors[sorted_indices][:num_colors]

    # Calculate brightness of each color (using the luminosity formula) and sort
    brightness = 0.299 * most_frequent_colors[:, 0] + 0.587 * most_frequent_colors[:, 1] + 0.114 * most_frequent_colors[:, 2]
    brightness_sorted_indices = np.argsort(brightness)
    
    # Return the colors sorted by brightness
    return most_frequent_colors[brightness_sorted_indices]

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


def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    num_clusters = 3
    # partitions = [[[0,0.5],[0,0.5]],[[0.5,1],[0,0.5]],[[0,0.5],[0.5,1]],[[0.5,1],[0.5,1]]]
    # partitions = [[[0,1],[0,0.5]],[[0,1],[0.5,1]]]
    partitions = [[[0,1],[0,1]]]

    if config["show_visual"]:
        root = tk.Tk()  
        root.title("Cluster Colors")
        window_height = 200
        window_width = 200
        root.geometry(f"{window_width}x{window_height}")  # Set the window size to be big enough to hold all partitions

        canvas = tk.Canvas(root, width=window_width, height=window_height)
        canvas.pack()

    if config["use_nanoleaf"]:
        panel_ids = get_panel_ids()
        num_clusters = len(panel_ids)

    while True:
        screen = ImageGrab.grab(all_screens=True)
        screen_partitions = split_image(screen, partitions)
        if config["show_visual"]:
            canvas.delete("all")  # Clear the canvas before redrawing
        hex_colors = []

        for partition, screen_partition in zip(partitions, screen_partitions):
            screen_partition = resize_image(screen_partition)
            dom_colors = quantize_color_and_sort_by_brightness(screen_partition, 20, num_clusters)
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
                    color_height = partition_height / len(dom_colors)
                    color_top = top + (i * color_height)
                    color_bottom = top + ((i + 1) * color_height)
                    color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
                    hex_colors.append(color_hex)
                    canvas.create_rectangle(left, color_top, right, color_bottom, fill=color_hex, outline=color_hex)

        if config["use_nanoleaf"]:
            panel_colors = {}   
            for panel_id_, i in zip(panel_ids,range(len(panel_ids))):
                panel_colors[panel_id_] = hex_colors[i]
            set_individual_panel_colors(panel_colors)
            # set_individual_panel_colors({35422: hex_colors[2], 57011: hex_colors[3], 33728: hex_colors[1]})

        if config["show_visual"]:
            root.update_idletasks()
            root.update()
        # time.sleep(0.2)


if __name__ == "__main__":
    main()
