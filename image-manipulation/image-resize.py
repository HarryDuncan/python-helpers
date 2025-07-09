from PIL import Image
import os

def resize_images_in_folder(folder_path, resize_factor):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            image_path = os.path.join(folder_path, filename)
            with Image.open(image_path) as img:
                new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
                resized_img = img.resize(new_size, Image.ANTIALIAS)
                new_filename = f"{os.path.splitext(filename)[0]}-resized.jpg"
                new_image_path = os.path.join(folder_path, new_filename)
              
                resized_img.save(new_image_path)
                print(f"Saved resized image as {new_filename}")


resize_images_in_folder('C:/Users/harry/Projects/art-os/public/assets/textures/emergence', 0.5)
