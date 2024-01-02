import colorsys
import os
import numpy as np
from screencap import capture_screen_scaled

script_dir = os.path.dirname(os.path.abspath(__file__))

def rgb_to_hsv(rgb_color):
    """
    Convert an RGB color to HSV color space.
    """
    # Normalize the RGB values by dividing by 255
    r, g, b = [x / 255.0 for x in rgb_color]
    return colorsys.rgb_to_hsv(r, g, b)

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

def significant_color_change(new_colors, color_history, threshold=10):
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

def is_color_greyish(color, grey_tolerance=20):
    """
    Check if a color is close to grey.
    A color is considered 'greyish' if the R, G, and B values are within a certain range of each other.
    """
    r, g, b = color
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    return (max_val - min_val) <= grey_tolerance

def sort_colors_by_hue(colors):
    """
    Sort a list of RGB colors by their hue value in HSV color space.
    """
    # Convert RGB colors to HSV
    hsv_colors = [rgb_to_hsv(color) for color in colors]
    # Sort colors by the hue value
    hsv_colors.sort(key=lambda color: color[0])
    # Convert back to RGB to return
    new_colors = [colorsys.hsv_to_rgb(*color) for color in hsv_colors]
    new_colors = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in new_colors]
    return new_colors

def calculate_luminosity(color):
    """Calculate the luminosity of a given RGB color."""
    # if isinstance(color, str):
    #     color = hex_to_rgb(color)
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

def sort_colors_by_luminosity(colors):
    """Sort a list of RGB colors by luminosity."""
    return sorted(colors, key=calculate_luminosity, reverse=True)

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

def quantize_color_and_sort_by_brightness(image, bin_size, color_history, num_colors=5, similarity_threshold=30, min_color_amnt=16, less_sensitive=False):
    """
    outputs the most interesting colors.
    """
    contrast = calculate_color_contrast_level(image)
    similarity_threshold = similarity_threshold + (contrast / 1000)

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
    
    unique_colors = sort_colors_by_luminosity([hex_to_rgb(color) if isinstance(color, str) else color for color in unique_colors])
    # If there's a significant color change, update the color history
    if not less_sensitive or significant_color_change(unique_colors, color_history):
        # if config["less_sensitive"]:
            # update_color_history(unique_colors)
        return unique_colors[:num_colors]
    else:
        # Return the last known good color set if no significant change
        return color_history[-1][:num_colors] if color_history else unique_colors[:num_colors]

def get_colors_from_screen(bin_size, color_history, num_colors=5, similarity_threshold=30, min_color_amnt=16, less_sensitive=False, screen_height=1080, screen_width=1920):
    screen = capture_screen_scaled(screen_width, screen_height)
    return quantize_color_and_sort_by_brightness(screen, bin_size, color_history, num_colors, similarity_threshold, min_color_amnt, less_sensitive)

def get_colors_from_image(image, bin_size, color_history, num_colors=5, similarity_threshold=30, min_color_amnt=16, less_sensitive=False):
    return quantize_color_and_sort_by_brightness(image, bin_size, color_history, num_colors, similarity_threshold, min_color_amnt, less_sensitive)