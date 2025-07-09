from moviepy.editor import VideoFileClip

def compress_video(input_path, output_path, target_resolution=(640, 360), bitrate="500k"):
    # Load the video
    video = VideoFileClip(input_path)
    
    # Resize the video
    video_resized = video.resize(newsize=target_resolution)
    
    # Save the video with reduced bitrate
    video_resized.write_videofile(output_path, bitrate=bitrate, codec='libx264')

# Usage
input_video_path = "C:/Users/harry/Videos/Workouts/glutes.mp4"
output_video_path = "C:/Users/harry/Videos/Workouts/ad/glutes.mp4"

compress_video(input_video_path, output_video_path)