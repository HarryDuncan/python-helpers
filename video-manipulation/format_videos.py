from moviepy.video.io.VideoFileClip import VideoFileClip
import os
import json

def trim_video(input_path, output_folder, output_name, duration):
    os.makedirs(output_folder, exist_ok=True)

    clip = VideoFileClip(input_path)
    total_duration = clip.duration
    start_time = max(0, (total_duration - duration) / 2)
    end_time = start_time + duration

    trimmed_clip = clip.subclip(start_time, end_time)
    output_path = os.path.join(output_folder, f"{output_name}.mp4")
    trimmed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", preset="placebo")

def process_folder(folder_path, output_folder, output_name, duration):
    # Get all MP4 files in the specified folder
    mp4_files = [file for file in os.listdir(folder_path) if file.lower().endswith(".mp4")]

    for index, mp4_file in enumerate(mp4_files):
        mp4_path = os.path.join(folder_path, mp4_file)
        trim_video(mp4_path, output_folder, f"{output_name}_{index}", duration)


with open("input_data.json", "r") as file:
    input_data = json.load(file)

    folder_path = input_data["folder_path"]
    output_folder = input_data["output_folder"]
    output_name = input_data["output_name"]
    duration = input_data["duration"]

    process_folder(folder_path, output_folder, output_name, duration)