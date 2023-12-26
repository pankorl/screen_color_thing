import numpy as np
from PIL import ImageGrab, Image
from sklearn.cluster import KMeans
import tkinter as tk
import time

def get_dominant_color(image, k=5, resize_factor=0.1):
    # Resize image to reduce computation
    image = image.resize((int(image.width * resize_factor), int(image.height * resize_factor)))
    # Convert image to numpy array
    np_image = np.array(image)

    # Reshape it to a list of pixels
    pixels = np_image.reshape(-1, np_image.shape[-1])

    # Using KMeans to cluster pixels
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)

    # Count labels to find most common cluster
    unique, counts = np.unique(kmeans.labels_, return_counts=True)
    dominant_color = kmeans.cluster_centers_[unique[np.argmax(counts)]]

    return dominant_color


def get_median_color(image):
    np_image = np.array(image)
    median_color = np.median(np_image.reshape(-1, np_image.shape[-1]), axis=0)
    return median_color

def get_average_color(image):
    np_image = np.array(image)
    average_color = np.mean(np_image, axis=(0, 1))
    return average_color

def capture_screen_rim(width, height, rim_width):
    screen = ImageGrab.grab(all_screens=True)
    left = screen.crop((0, 0, rim_width, height))
    right = screen.crop((width - rim_width, 0, width, height))
    top = screen.crop((0, 0, width, rim_width))
    bottom = screen.crop((0, height - rim_width, width, height))
    return left, right, top, bottom

def update_color_display(window, color):
    color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
    window.config(bg=color_hex)

def main():
    rim_width = 100

    # Set up the Tkinter window
    window = tk.Tk()
    window.title("Average Screen Color")
    window.geometry("200x200")

    i = 0
    while True:
        # width, height = ImageGrab.grab().size
        screen = ImageGrab.grab(all_screens=True)
        # left, right, top, bottom = capture_screen_rim(width, height, rim_width)
        # avg_colors = [get_average_color(region) for region in [left, right, top, bottom]]
        # overall_avg_color = np.mean(avg_colors, axis=0)
        # update_color_display(window, overall_avg_color)

        # avg_color = get_average_color(screen)
        # # avg_color = get_median_color(screen)

        # update_color_display(window, avg_color)
        # window.update_idletasks()
        # window.update()

        dom_color = get_dominant_color(screen)
        update_color_display(window, dom_color)
        window.update_idletasks()
        window.update()
        
        time.sleep(0.1)
        i+=1
        print(i)

if __name__ == "__main__":
    main()
