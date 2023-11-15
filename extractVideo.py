import sys
from moviepy.editor import VideoFileClip
import os

def remove_audio_from_video(input_video_path):
    """
    Remove all audio tracks from an MP4 video file.

    Args:
    input_video_path (str): Path to the input video file.
    """
    # Extracting filename and extension
    base, ext = os.path.splitext(input_video_path)
    output_video_path = f"{base}_noAudio{ext}"

    # Load the video file
    video = VideoFileClip(input_video_path)
    
    # Remove audio
    video_no_audio = video.without_audio()
    
    # Write the result to the output file
    video_no_audio.write_videofile(output_video_path, codec="libx264", audio_codec=None)
    print(f"Output saved as {output_video_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_video>")
        sys.exit(1)

    input_video = sys.argv[1]
    remove_audio_from_video(input_video)
