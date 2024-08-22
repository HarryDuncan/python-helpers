from PIL import Image, ImageEnhance
import requests
from io import BytesIO
import random

def shift_hue(image, shift_factor):
    # Convert the image to the HSV color space
    hsv_image = image.convert('HSV')

    # Extract the H, S, and V channels
    h, s, v = hsv_image.split()

    # Calculate the shift value based on the shift_factor
    shift_value = int(255 * shift_factor)

    # Shift the hue channel
    h = h.point(lambda i: (i + shift_value) % 256)

    # Merge the channels back to form the new image
    shifted_image = Image.merge('HSV', (h, s, v)).convert('RGB')

    return shifted_image

def even_hue_shift(image, num_variations):
    result_images = []
    hue_range = 1.0  # Hue values typically range from 0.0 to 1.0 in Pillow

    for i in range(num_variations):
        # Calculate the hue shift factor
        hue_shift_factor = i / num_variations

        # Apply the hue shift
        shifted_image = shift_hue(image, hue_shift_factor)

        result_images.append(shifted_image)

    return result_images

def main(image_url, num_variations):
    
    # Load the image from the local file path
    original_image = Image.open(image_url)


    # Perform random hue shifts
    result_images =  even_hue_shift(original_image, num_variations)

    # Save the resulting images as JPG files
    for i, result_image in enumerate(result_images):
        result_image.save(f"si{i + 1}.jpg", format="JPEG")

if __name__ == "__main__":
    image_url = "C:/Users/harry/Projects/art-os/public/assets/textures/matcaps/wormhole-2.jpg"  # Replace with the actual URL of the image
    num_variations = 15  # Adjust the number of variations as needed

    main(image_url, num_variations)