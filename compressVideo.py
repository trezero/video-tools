import subprocess
import sys
import os

def compress_video(input_path, output_path, target_size_MB, crf_value=23):
    """
    Compresses a video file to a target size with as much quality retention as possible.
    
    Args:
    input_path (str): Path to the input video file.
    output_path (str): Path where the compressed video will be saved.
    target_size_MB (int): Target size in megabytes for the output video.
    crf_value (int): Constant Rate Factor for quality (default is 23, the range is 0-51, where lower numbers are higher quality).
    """
    
    # Calculate target bitrate based on the desired size (in bits)
    duration_seconds = float(subprocess.check_output(
        f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_path}"',
        shell=True))
    target_total_bitrate = (target_size_MB * 8 * 1024 * 1024) / duration_seconds
    
    # Audio bitrate to subtract from target total bitrate to get video bitrate
    audio_bitrate = 128000  # This is a good default for decent quality audio

    # Calculate video bitrate
    video_bitrate = target_total_bitrate - audio_bitrate

    if video_bitrate <= 0:
        print("Error: Target size too low to accommodate even audio bitrate.")
        sys.exit(1)
    
    # Build and run ffmpeg command
    cmd = (
        f'ffmpeg -i "{input_path}" -b:v {int(video_bitrate)} -crf {crf_value} '
        f'-b:a {int(audio_bitrate)} -preset slower "{output_path}"'
    )
    subprocess.run(cmd, shell=True)
    
    # Verify that file has been created
    if not os.path.isfile(output_path):
        print("Error: Compression failed, output file not created.")
        sys.exit(1)
    else:
        print(f"Compression successful. File saved at {output_path}")

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) != 3:
        print("Usage: python compress_video.py input_path target_size_MB")
        sys.exit(1)

    input_path = sys.argv[1]
    target_size_MB = int(sys.argv[2])
    
    # Output path is the same as the input with "_compressed" appended
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_compressed{ext}"

    compress_video(input_path, output_path, target_size_MB)
