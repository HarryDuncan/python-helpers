from PIL import Image

# Load the original image
img = Image.open('8bytes.jpg')

width, height = img.size

# Calculate the width and height of each face of the cube
face_width = width // 3
face_height = height // 3

# Split the image into six faces of the cube
left_face = img.crop((0, face_height, face_width, 2*face_height))
right_face = img.crop((2*face_width, face_height, 3*face_width, 2*face_height))
top_face = img.crop((face_width, 0, 2*face_width, face_height))
bottom_face = img.crop((face_width, 2*face_height, 2*face_width, height))
front_face = img.crop((face_width, face_height, 2*face_width, 2*face_height))
back_face = img.crop((2*face_width, 0, 3*face_width, face_height))

# Save each face as a separate image
left_face.save('processed/left_face.jpg')
right_face.save('processed/right_face.jpg')
top_face.save('processed/top_face.jpg')
bottom_face.save('processed/bottom_face.jpg')
front_face.save('processed/front_face.jpg')
back_face.save('processed/back_face.jpg')