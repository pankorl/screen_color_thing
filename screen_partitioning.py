import io
from PIL import Image


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