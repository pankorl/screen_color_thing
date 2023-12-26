import cv2
import numpy as np
from PIL import ImageGrab, Image
import tkinter as tk
import time
import io

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

def update_color_display(window, color):
    color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
    window.config(bg=color_hex)

def main():
    num_clusters = 2
    partitions = [[[0,0.5],[0,0.5]],[[0.5,1],[0,0.5]],[[0,0.5],[0.5,1]],[[0.5,1],[0.5,1]]]
    
    windows = []
    for i in range(num_clusters):
        for j in range(len(partitions)):
            window = tk.Tk()
            window.title(f"{i} {j}")
            window.geometry("200x200")
            windows.append(window)

    i = 0
    while True:
        screen = ImageGrab.grab(all_screens=True)
        screen_partitions = split_image(screen, partitions)
        for screen_partition, i in zip(screen_partitions, range(len(screen_partitions))):
            # screen_partition.save(f"{i}.png")
            dom_colors = get_dominant_color(screen_partition, k=num_clusters, resize_factor=0.1)
            for window, j in zip(windows[i*num_clusters:i*num_clusters+num_clusters], range(num_clusters)):
                update_color_display(window, dom_colors[j])
                window.update_idletasks()
                window.update()
        i += 1
        # print(i)
        time.sleep(0.2)

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

if __name__ == "__main__":
    main()
