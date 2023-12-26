import cv2
import numpy as np
from PIL import ImageGrab
import tkinter as tk
import time

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
    num_clusters = 3
    
    windows = []
    for i in range(num_clusters):
        window = tk.Tk()
        window.title(i)
        window.geometry("200x200")
        windows.append(window)

    i = 0
    while True:
        screen = ImageGrab.grab(all_screens=True)
        dom_colors = get_dominant_color(screen, k=num_clusters)
        for window, i in zip(windows, range(num_clusters)):
            update_color_display(window, dom_colors[i])
            window.update_idletasks()
            window.update()
        i += 1
        # print(i)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
