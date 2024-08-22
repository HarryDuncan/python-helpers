import os
import random
import cv2
import numpy as np

def shift_hue(frame, shift_factor):
    # Convert the frame to the HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)

    # Extract the H, S, and V channels
    h, s, v = cv2.split(hsv_frame)

    # Calculate the shift value based on the shift_factor
    shift_value = (179 * shift_factor)

    # Shift the hue channel
    h = (h + shift_value) % 180

    # Merge the channels back to form the new frame
    shifted_frame = cv2.merge([h, s, v])

    # Convert the frame back to the BGR color space
    shifted_frame = cv2.cvtColor(shifted_frame.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return shifted_frame

def add_ripple_effect(frame, ripple_strength=0.1):
    # Convert the frame to the HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Extract the H, S, and V channels
    h, s, v = cv2.split(hsv_frame)

    # Add a ripple effect using a sine function
    rows, cols = h.shape[:2]
    for i in range(rows):
        h[i, :] = np.roll(h[i, :], int(ripple_strength * np.sin(2 * np.pi * i / ripple_strength)))

    # Merge the channels back to form the new frame
    distorted_frame = cv2.merge([h, s, v])

    # Convert the frame back to the BGR color space
    distorted_frame = cv2.cvtColor(distorted_frame, cv2.COLOR_HSV2BGR)

    return distorted_frame

def even_hue_shift_video(video_path, output_directory, num_variations):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get the video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create VideoWriter object to save the output video
    output_filename = 'output.mp4'
    output_path = os.path.join(output_directory, output_filename)
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    frame_counter = 0
    hue_range = 1.0  # Hue values typically range from 0.0 to 1.0 in OpenCV
   
    hue_shift_value = random.uniform(0, hue_range)
    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        # Break the loop if the video has ended
        if not ret:
            break
        # Write the processed frame to the output video
       

        shifted_frame = shift_hue(frame, hue_shift_value)
        shifted_frame = add_ripple_effect(shifted_frame, ripple_strength=2.1)
        out.write(shifted_frame)
        frame_counter += 1
        # Display the original and shifted frames (optional)
        cv2.imshow('Original Frame', frame)
        cv2.imshow('Shifted Frame', shifted_frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and writer objects
    cap.release()
    out.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = "C:/Users/harry/Videos/Loop1.mp4"  # Replace with the actual path of your input video
    output_path = "C:/Users/harry/Videos/barba/formatted"  # Replace with the desired output video path
    num_variations = 15  # Adjust the number of variations as needed

    even_hue_shift_video(video_path, output_path, num_variations)
