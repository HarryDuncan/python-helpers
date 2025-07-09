from PIL import Image, ImageDraw, ImageFont
import os
import re
def create_word_images(text, font_path, font_size=48, text_color="white", output_dir="word_images"):
    """
    Creates PNG images for each word in the given text.
    
    Args:
        text (str): The input text.
        font_path (str): Path to the .ttf font file.
        font_size (int): Font size for the text.
        text_color (str or tuple): Color of the text (e.g., "black" or (255, 0, 0)).
        output_dir (str): Directory to save the images.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font file not found: {font_path}")
        return

    # Generate images for each word
    words = text.split()
    for i, word in enumerate(words, start=1):
        # Create a temporary image to get text size
        temp_image = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(temp_image)
        text_width, text_height = draw.textsize(word, font=font)

        # Create a new image with the correct size
        image = Image.new("RGBA", (text_width + 10, text_height + 10), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.text((5, 5), word, font=font, fill=text_color)

        # Save the image
        output_path = os.path.join(output_dir, f"word_{i:03d}_{re.sub('[^A-Za-z0-9]+', '', word)}.png")
        image.save(output_path)
        print(f"Saved: {output_path}")

# Example usage
if __name__ == "__main__":
    input_text = "REPRODUCTION IT'S REDEFINE LIFE ITSELF"
    font_file = "HarryDuncan.ttf"  # Replace with the path to your .ttf font file
    create_word_images(input_text, font_file, font_size=170, text_color="white", output_dir="output_images")
